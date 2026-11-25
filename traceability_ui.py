import hashlib,io,json,os
from datetime import datetime,timezone
from urllib.parse import urlencode
import streamlit as st
import qrcode
from web3 import Web3
from blockchain_client import connect,product_id,send,STAGES,NEXT,ZERO
from chain_explorer import render_chain
from passport_links import passport_url,qr_png

def render():
    st.title('Product passports')
    st.caption('Local Ethereum · Product identity, lifecycle history and confirmed custody transfers')
    try:w,c=connect()
    except Exception as e:
        st.info(str(e));st.code('npm install\nnpm run compile\nnpm run chain\n# In another terminal:\npython scripts/deploy.py',language='shell');return
    st.caption(f'Chain {w.eth.chain_id} · Contract {c.address} · Latest block {w.eth.block_number}')
    render_chain(w,c)
    with st.expander('Development network details'):
        st.write('These are unlocked local demo accounts. Selecting one simulates a participant; it is not production authentication. No real funds are used. Blockchain records do not prove physical identity or truthful inputs.')
    accounts=w.eth.accounts
    actor=st.selectbox('Act as local demo participant',accounts,format_func=lambda x:f'Participant {accounts.index(x)+1} · {x[:8]}…{x[-6:]}',key='passport_actor')
    if 'passport_receipt' in st.session_state:
        tx,block=st.session_state.passport_receipt;st.success(f'Confirmed in block {block}');st.code(tx,language=None)
    with st.expander('Register a product'):
        with st.form('register_passport'):
            ref=st.text_input('Unique product reference',help='Use an opaque public reference. Do not enter personal information.')
            label=st.text_input('Public product label',max_chars=120)
            kind=st.selectbox('Device category',['Smartphone','Laptop','Television','Lithium-ion Battery','Desktop Computer','Printer','Monitor','Keyboard'])
            evidence=st.file_uploader('Optional evidence file — only its SHA-256 hash is recorded',key='registration_evidence')
            submitted=st.form_submit_button('Register on blockchain')
        if submitted:
            try:
                if not ref.strip() or not label.strip():raise ValueError('Enter a product reference and label.')
                digest=hashlib.sha256(evidence.getvalue()).digest() if evidence else bytes(32)
                st.session_state.passport_receipt=send(w,c.functions.register(product_id(ref),label.strip(),kind,digest),actor)
                st.session_state.passport_lookup=ref.strip();st.rerun()
            except Exception as e:st.error(str(e))
    count=c.functions.productCount().call()
    st.caption(f'{count} registered products')
    if count:
        with st.expander('Browse passports'):
            ids=[Web3.to_hex(c.functions.productIdAt(i).call()) for i in range(min(count,100))]
            selected=st.selectbox('Product ID',ids,key='browse_passport')
            if st.button('Open selected passport'):st.session_state.passport_lookup=selected;st.rerun()
            if count>100:st.caption('Showing first 100. Use exact ID lookup for others.')
    incoming=st.query_params.get('product','')
    if incoming and incoming!=st.session_state.get('_last_passport_link'):
        st.session_state.passport_lookup=incoming
        st.session_state._last_passport_link=incoming
    if 'passport_lookup' not in st.session_state:st.session_state.passport_lookup=''
    expected_chain=st.query_params.get('chain')
    expected_contract=st.query_params.get('contract')
    if (expected_chain and expected_chain!=str(w.eth.chain_id)) or (expected_contract and expected_contract.lower()!=c.address.lower()):
        st.error('This QR belongs to a different blockchain deployment. Connect to its original network and contract to view the passport.');return
    lookup=st.text_input('Trace a product reference or blockchain ID',key='passport_lookup')
    if not lookup.strip():return
    try:pid=product_id(lookup);p=c.functions.getProduct(pid).call()
    except Exception:st.warning('No passport found for this reference on the current contract.');return
    pid_hex=Web3.to_hex(pid)
    a,b=st.columns([2,1])
    base=os.getenv('RECLAIM_PASSPORT_BASE_URL')
    if not base:
        try:base=st.secrets.get('passport_base_url','http://127.0.0.1:8501')
        except FileNotFoundError:base='http://127.0.0.1:8501'
    base=base.rstrip('/')
    try:url=passport_url(base,pid_hex,w.eth.chain_id,c.address)
    except ValueError as exc:st.error(str(exc));return
    with a:
        st.subheader(p[0]);st.write(f'{p[1]} · {STAGES[p[4]]}')
        st.caption('Blockchain product ID');st.code(pid_hex,language=None)
        st.write('Current custodian');st.code(p[2],language=None)
        if p[3]!=ZERO:st.write('Pending recipient: '+p[3])
        st.link_button('Open passport link',url)
        st.caption('The app and original blockchain must be running. This link identifies the product, chain and contract.')
        if '127.0.0.1' in base or 'localhost' in base:
            st.info('Computer-only QR: this address cannot open on your phone. A phone-accessible passport address is not configured.')
        else:
            st.caption('For a Wi-Fi address, connect your phone to the same network as this computer. Keep the passport viewer and blockchain running.')
        with st.expander('QR destination'):
            st.code(url,language=None)
    with b:
        png=qr_png(url)
        st.image(png,width=280)
        st.download_button('Download product QR',png,'reclaim-'+pid_hex[2:14]+'.png','image/png')
    if actor.lower()==p[2].lower():
        with st.expander('Owner actions'):
            if p[4]!=4 and p[3]==ZERO:
                recipient=st.selectbox('Recipient', [x for x in accounts if x!=actor],key='handoff_recipient')
                if st.button('Propose custody transfer'):
                    transact(w,c.functions.proposeTransfer(pid,recipient),actor)
            elif p[3]!=ZERO:
                if st.button('Cancel pending transfer'):transact(w,c.functions.cancelTransfer(pid),actor)
            with st.form('passport_event'):
                available=NEXT[p[4]] if p[3]==ZERO else []
                options=['Append note']+[STAGES[x] for x in available]
                action=st.selectbox('Lifecycle event',options)
                detail=st.text_area('Public event details',max_chars=500,help='Corrections are new notes. Existing events cannot be edited.')
                evidence=st.file_uploader('Optional evidence file — hash only',key='event_evidence')
                submit=st.form_submit_button('Record event on blockchain')
            if submit:
                if not detail.strip():st.error('Enter event details.')
                else:
                    digest=hashlib.sha256(evidence.getvalue()).digest() if evidence else bytes(32)
                    fn=c.functions.appendNote(pid,detail.strip(),digest) if action=='Append note' else c.functions.updateStage(pid,STAGES.index(action),detail.strip(),digest)
                    transact(w,fn,actor)
    elif actor.lower()==p[3].lower():
        st.info('This participant is the nominated recipient. Ownership changes only after acceptance.')
        if st.button('Accept custody transfer'):transact(w,c.functions.acceptTransfer(pid),actor)
    st.subheader('Verified on-chain history')
    n=c.functions.historyCount(pid).call()
    rows=[]
    for i in reversed(range(n)):
        event=c.functions.historyAt(pid,i).call()
        stamp=datetime.fromtimestamp(event[0],timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        rows.append({'timestamp':stamp,'actor':event[1],'action':event[2],'details':event[3],'evidence_sha256':Web3.to_hex(event[4])})
        with st.container(border=True):
            st.write(event[2]+' · '+stamp);st.write(event[3]);st.caption('Recorded by '+event[1])
            if event[4]!=bytes(32):st.code('SHA-256: '+event[4].hex(),language=None)
    st.download_button('Export passport history',json.dumps({'chain_id':1337,'contract':c.address,'product_id':pid_hex,'events':list(reversed(rows))},indent=2),'passport.json','application/json')
    with st.expander('Verify an evidence file'):
        check=st.file_uploader('Select the original file',key='verify_passport_evidence')
        if check:
            digest=hashlib.sha256(check.getvalue()).hexdigest()
            matched=any(r['evidence_sha256'].lower()=='0x'+digest for r in rows)
            st.success('SHA-256 matches a recorded evidence hash.') if matched else st.warning('No matching evidence hash in this passport.')

def transact(w,fn,actor):
    try:st.session_state.passport_receipt=send(w,fn,actor);st.rerun()
    except Exception as e:st.error(str(e))
