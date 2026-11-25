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
    st.title('Product journey')
    st.write('Find a device, see what happened to it, and record its next step.')
    try:w,c=connect()
    except Exception as e:
        st.warning('The local blockchain is offline. Start it to load product journeys.')
        with st.expander('Setup instructions'):
            st.write(str(e));st.code('npm run chain\n# In another terminal:\npython scripts/deploy.py',language='shell')
        return
    with st.expander('New to blockchain? Start here'):
        st.write('A product passport is a shared logbook for one device. Registration starts its story; collection, inspection, repair and recycling add new entries.')
        st.write('Each saved action is a transaction. Transactions are stored in numbered blocks, linked together using digital fingerprints. Corrections are added as new notes, so the earlier entries stay visible.')
        st.caption('This is a local demonstration. It records what participants submit; it cannot check whether a physical device or inspection is genuine.')
    accounts=w.eth.accounts
    with st.expander('Demo participant and network settings'):
        st.caption('Switch participants to try a handover. These are simulated accounts, without sign-in or real funds.')
        actor=st.selectbox('Use the app as',accounts,format_func=lambda x:f'Participant {accounts.index(x)+1}',key='passport_actor')
        st.code(actor,language=None)
        st.caption(f'Local Ethereum · Chain {w.eth.chain_id} · Latest block {w.eth.block_number}')
        st.code('Contract: '+c.address,language=None)
    def participant(address):
        return f'Participant {accounts.index(address)+1}' if address in accounts else address[:8]+'…'+address[-6:]
    if 'passport_receipt' in st.session_state:
        tx,block=st.session_state.passport_receipt
        st.success(f'Saved to the blockchain in block #{block}.')
        with st.expander('View save receipt'):st.code(tx,language=None)
    st.subheader('Find a product')
    with st.expander('Add a new product'):
        st.caption('Create its passport once. You can add updates after registration.')
        with st.form('register_passport'):
            ref=st.text_input('Product reference',placeholder='For example, DEVICE-001',help='Use an opaque public reference. Do not enter personal information.')
            label=st.text_input('Product name',max_chars=120)
            kind=st.selectbox('Device category',['Smartphone','Laptop','Television','Lithium-ion Battery','Desktop Computer','Printer','Monitor','Keyboard'])
            evidence=st.file_uploader('Optional evidence file — only its SHA-256 hash is recorded',key='registration_evidence')
            submitted=st.form_submit_button('Create product passport')
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
        with st.expander('Choose a registered product',expanded=not bool(st.query_params.get('product') or st.session_state.get('passport_lookup'))):
            ids=[Web3.to_hex(c.functions.productIdAt(i).call()) for i in range(min(count,100))]
            names={i:c.functions.getProduct(bytes.fromhex(i[2:])).call()[0] for i in ids}
            selected=st.selectbox('Registered products',ids,format_func=lambda i:names[i]+' · '+i[2:8],key='browse_passport')
            if st.button('View product journey'):st.session_state.passport_lookup=selected;st.rerun()
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
    lookup=st.text_input('Or enter a product reference',placeholder='For example, DEVICE-001',key='passport_lookup')
    if not lookup.strip():
        st.info('Choose a registered product above, or add a new product to begin.')
        with st.expander('Explore how the blockchain works'):render_chain(w,c)
        return
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
        st.subheader(p[0]);st.write(f'{p[1]} · **{STAGES[p[4]]}**')
        explanations=['Its passport has been created. Collection has not been recorded yet.','Collection has been recorded. Inspection is the next step.','Inspection has been recorded. The holder can record repair or recycling.','Repair has been recorded. The device can return for collection or inspection.','Recycling has been recorded. This is the final lifecycle stage.']
        st.caption(explanations[p[4]])
        st.write('Currently held by **'+participant(p[2])+'**')
        if p[3]!=ZERO:st.info('Waiting for '+participant(p[3])+' to accept the handover.')
        with st.expander('Product identifiers'):
            st.caption('Product ID');st.code(pid_hex,language=None)
            st.caption('Holder’s blockchain address');st.code(p[2],language=None)
        st.link_button('Open read-only passport',url)
        st.caption('The app and original blockchain must be running. This link identifies the product, chain and contract.')
        if '127.0.0.1' in base or 'localhost' in base:
            st.info('Computer-only QR: this address cannot open on your phone. A phone-accessible passport address is not configured.')
        else:
            st.caption('For a Wi-Fi address, connect your phone to the same network as this computer. Keep the passport viewer and blockchain running.')
        with st.expander('QR destination'):
            st.code(url,language=None)
    with b:
        st.caption('Scan to view this product on your phone')
        png=qr_png(url)
        st.image(png,width=280)
        st.download_button('Download product QR',png,'reclaim-'+pid_hex[2:14]+'.png','image/png')
    if actor.lower()==p[2].lower():
        with st.expander('Update this product',expanded=True):
            st.caption('You are acting as the current holder. Updates are saved as new entries.')
            if p[4]!=4 and p[3]==ZERO:
                recipient=st.selectbox('Hand over to', [x for x in accounts if x!=actor],format_func=participant,key='handoff_recipient')
                if st.button('Request handover'):
                    transact(w,c.functions.proposeTransfer(pid,recipient),actor)
            elif p[3]!=ZERO:
                if st.button('Cancel handover request'):transact(w,c.functions.cancelTransfer(pid),actor)
            with st.form('passport_event'):
                available=NEXT[p[4]] if p[3]==ZERO else []
                options=['Append note']+[STAGES[x] for x in available]
                action=st.selectbox('What happened to the device?',options)
                detail=st.text_area('Describe what happened',max_chars=500,help='Corrections are new notes. Existing events cannot be edited.')
                evidence=st.file_uploader('Optional evidence file — hash only',key='event_evidence')
                submit=st.form_submit_button('Save update to blockchain')
            if submit:
                if not detail.strip():st.error('Enter event details.')
                else:
                    digest=hashlib.sha256(evidence.getvalue()).digest() if evidence else bytes(32)
                    fn=c.functions.appendNote(pid,detail.strip(),digest) if action=='Append note' else c.functions.updateStage(pid,STAGES.index(action),detail.strip(),digest)
                    transact(w,fn,actor)
    elif actor.lower()==p[3].lower():
        st.info('This participant is the nominated recipient. Ownership changes only after acceptance.')
        if st.button('Accept this handover'):transact(w,c.functions.acceptTransfer(pid),actor)
    else:
        st.caption('To add an update, select '+participant(p[2])+' in Demo participant and network settings.')
    st.subheader('Recorded journey')
    st.caption('Newest entries first. These are statements saved on the blockchain, not independent physical inspections.')
    n=c.functions.historyCount(pid).call()
    rows=[]
    for i in reversed(range(n)):
        event=c.functions.historyAt(pid,i).call()
        stamp=datetime.fromtimestamp(event[0],timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        rows.append({'timestamp':stamp,'actor':event[1],'action':event[2],'details':event[3],'evidence_sha256':Web3.to_hex(event[4])})
        with st.container(border=True):
            title={'Registered':'Passport created','Transfer proposed':'Handover requested','Transfer accepted':'Handover accepted','Transfer cancelled':'Handover cancelled','Note':'Note added'}.get(event[2],event[2])
            st.write('**'+title+'**');st.caption(stamp+' · '+participant(event[1]))
            st.write('Requested handover to '+participant(Web3.to_checksum_address(event[3])) if event[2]=='Transfer proposed' else event[3])
            if event[4]!=bytes(32):
                with st.expander('Evidence fingerprint'):st.code(event[4].hex(),language=None)
    with st.expander('Explore the blockchain behind this journey'):render_chain(w,c)
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
