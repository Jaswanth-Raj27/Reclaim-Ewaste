"""Read real local EVM blocks and mine an explicit empty development block."""
import html
from datetime import datetime,timezone
import streamlit as st
from web3 import Web3

def mine_development_block(w):
    if w.eth.chain_id!=1337:raise RuntimeError('Manual mining is restricted to local development chain 1337.')
    previous=w.eth.block_number
    result=w.provider.make_request('evm_mine',[])
    if result.get('error'):raise RuntimeError(result['error'].get('message','Mining failed'))
    latest=w.eth.get_block('latest')
    if latest.number<=previous:raise RuntimeError('No new block was confirmed.')
    return latest

def verify_chain(w):
    """Check every parent link in a fixed snapshot; no claim of external consensus."""
    latest=w.eth.block_number
    prior=w.eth.get_block(0)
    for n in range(1,latest+1):
        block=w.eth.get_block(n)
        if block.parentHash!=prior.hash:raise ValueError(f'Block #{n} does not link to block #{n-1}.')
        prior=block
    if w.eth.get_block(latest).hash!=prior.hash:raise ValueError('The chain changed during the check. Please try again.')
    return latest

def render_chain(w,contract):
    latest=w.eth.block_number
    title,action=st.columns([2,1])
    with title:
        st.subheader('Your blockchain')
        st.caption(f'{latest+1} blocks saved on this computer')
    with action:
        if st.button('Check the chain',type='primary',use_container_width=True):
            try:
                with st.spinner('Checking every block…'):checked=verify_chain(w)
                st.session_state.chain_check=(checked,Web3.to_hex(w.eth.get_block(checked).hash))
            except Exception as exc:
                st.session_state.pop('chain_check',None);st.error('The check could not pass. '+str(exc))
    result=st.session_state.get('chain_check')
    if result:
        checked,fingerprint=result
        if checked<=latest and Web3.to_hex(w.eth.get_block(checked).hash)==fingerprint:
            st.success(f'All {checked} links match through block #{checked}. No broken links were found.')
            if latest>checked:st.caption('New blocks were added. Press Check the chain to include them.')
        else:st.warning('The chain has changed. Check it again.')
    st.caption('Checks that each block points to the one before it. This local check does not prove the device details are true or compare against an outside copy.')
    with st.expander('See the blocks'):
        render_block_details(w,contract,latest)

def render_block_details(w,contract,latest):
    # Limit rendering while retaining access to the complete existing chain.
    initial=max(0,latest-5)
    end=st.number_input('Show recent blocks ending at',min_value=0,max_value=latest,value=latest,step=1,key='chain_window_end_'+str(latest))
    numbers=list(range(max(0,end-5),end+1))
    blocks=[w.eth.get_block(n) for n in numbers]
    logs=contract.events.Recorded().get_logs(from_block=numbers[0],to_block=numbers[-1])
    app_events={}
    for log in logs:app_events.setdefault(log['blockNumber'],[]).append(log['args']['action'])
    selected=st.session_state.get('chain_selected',latest)
    items=[]
    for i,block in enumerate(blocks):
        hash_hex=Web3.to_hex(block.hash);parent=Web3.to_hex(block.parentHash)
        count=len(block.transactions)
        label='Genesis' if block.number==0 else ', '.join(app_events.get(block.number,[])) or ('Empty block' if not count else 'Other contract activity')
        stamp=datetime.fromtimestamp(block.timestamp,timezone.utc).strftime('%H:%M:%S UTC')
        is_new=block.number==st.session_state.get('new_chain_block')
        item=f'''<article class="chain-block {'new' if is_new else ''}" aria-label="Block {block.number}, {count} transactions, {html.escape(label)}">
<div class="block-number">Block #{block.number}</div><div class="block-kind">{html.escape(label)}</div>
<div class="block-meta">{count} transaction{'s' if count!=1 else ''} · {stamp}</div>
<div class="hash-label">This block’s fingerprint</div><code>{hash_hex[:12]}…{hash_hex[-6:]}</code>
<div class="hash-label">Previous block’s fingerprint</div><code>{parent[:12]}…{parent[-6:]}</code></article>'''
        if i:items.append('<div class="chain-link" aria-label="Linked by parent hash">→</div>')
        items.append(item)
    st.markdown('''<style>
    .chain-strip{display:flex;align-items:center;gap:10px;overflow-x:auto;padding:8px 0 18px}
    .chain-block{box-sizing:border-box;flex:1 0 160px;min-width:0;min-height:188px;background:#fff;border:1px solid #dfdcd7;border-radius:4px;padding:15px 14px;color:#232323}
    .chain-block.new{border:2px solid #B74936;background:#fff9f6}
    .block-number{font-size:18px;font-weight:500;margin-bottom:8px;font-variant-numeric:tabular-nums}
    .block-kind{font-size:13px;min-height:36px;line-height:1.4}.block-meta{font-size:11px;color:#6e6a65;margin:6px 0 12px}
    .hash-label{font-size:11px;color:#6e6a65;margin-top:7px}.chain-block code{font-size:11px;color:#494540;background:none;padding:0}
    .chain-link{color:#B74936;font-size:22px;flex:0 0 12px}
    </style><div class="chain-strip" role="region" aria-label="Existing blockchain, oldest to newest">'''+''.join(items)+'</div>',unsafe_allow_html=True)
    st.caption(f'Showing blocks {numbers[0]}–{numbers[-1]} of {latest+1} total, including genesis. Arrows show chronological order; each newer block stores the older block’s hash.')
    with st.expander('Check a block’s link and technical details'):
        chosen=st.number_input('Block number',min_value=0,max_value=latest,value=min(selected,latest),step=1,key='inspect_block_'+str(latest))
        block=w.eth.get_block(chosen,full_transactions=True)
        if chosen>0:
            prior=w.eth.get_block(chosen-1)
            if block.parentHash==prior.hash:st.success(f'Parent hash matches block #{chosen-1}.')
            else:st.error('Parent hash mismatch.')
        else:st.info('Genesis is the first block; it has no predecessor.')
        st.code('Block hash:  '+Web3.to_hex(block.hash)+'\nParent hash: '+Web3.to_hex(block.parentHash),language=None)
        st.write(f"Transactions: {len(block.transactions)} · Gas used: {block.gasUsed:,} · Timestamp: {datetime.fromtimestamp(block.timestamp,timezone.utc).isoformat()}")
        if not block.transactions:st.caption('This block contains no transactions and does not change a product passport.')
        for tx in block.transactions:
            st.code(Web3.to_hex(tx.hash),language=None)
            st.caption(f"From {tx['from']} → {tx['to'] or 'Contract creation'}")
            if tx['to'] and tx['to'].lower()==contract.address.lower():
                try:
                    function,args=contract.decode_function_input(tx['input'])
                    st.write('Contract operation: '+function.fn_name)
                    st.json({k:Web3.to_hex(v) if isinstance(v,bytes) else v for k,v in args.items()})
                except ValueError:st.caption('Unable to decode this transaction input.')
    st.divider()
