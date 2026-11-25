import hashlib,io,json,os
from datetime import datetime,timezone
from urllib.parse import urlencode
import streamlit as st
import qrcode
from web3 import Web3
from blockchain_client import connect,product_id,send,STAGES,NEXT,ZERO

def render():
    st.title('Product passports')
    st.caption('Local Ethereum · Product identity, lifecycle history and confirmed custody transfers')
    try:w,c=connect()
    except Exception as e:
        st.info(str(e));st.code('npm install\nnpm run compile\nnpm run chain\n# In another terminal:\npython scripts/deploy.py',language='shell');return
    st.caption(f'Chain {w.eth.chain_id} · Contract {c.address} · Latest block {w.eth.block_number}')
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
    if 'passport_lookup' not in st.session_state:st.session_state.passport_lookup=st.query_params.get('product','')
    lookup=st.text_input('Trace a product reference or blockchain ID',key='passport_lookup')
    if not lookup.strip():return
    try:pid=product_id(lookup);p=c.functions.getProduct(pid).call()
    except Exception:st.warning('No passport found for this reference on the current contract.');return
    pid_hex=Web3.to_hex(pid)
    a,b=st.columns([2,1])
    base=os.getenv('RECLAIM_PASSPORT_BASE_URL','http://127.0.0.1:8501').rstrip('/')
    url=base+'/?'+urlencode({'product':pid_hex})
    with a:
        st.subheader(p[0]);st.write(f'{p[1]} · {STAGES[p[4]]}')
        st.caption('Blockchain product ID');st.code(pid_hex,language=None)
        st.write('Current custodian');st.code(p[2],language=None)
        if p[3]!=ZERO:st.write('Pending recipient: '+p[3])
        st.caption('QR links require the app and the same node/deployment. A localhost link works only on this computer; the base URL is configurable for a future hosted app.')
    with b:
        qr=qrcode.make(url);buff=io.BytesIO();qr.save(buff,format='PNG');st.image(buff.getvalue(),width=150)
        st.download_button('Download product QR',buff.getvalue(),'reclaim-'+pid_hex[2:14]+'.png','image/png')
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
