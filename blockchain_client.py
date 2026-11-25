import json, os
from pathlib import Path
from urllib.parse import urlparse
from web3 import Web3

ROOT=Path(__file__).parent
STAGES=['Registered','Collected','Inspected','Repaired','Recycled']
NEXT={0:[1],1:[2],2:[3,4],3:[1,2],4:[]}
ZERO='0x'+'0'*40

def connect():
    rpc=os.getenv('RECLAIM_RPC_URL','http://127.0.0.1:8545')
    if urlparse(rpc).hostname not in {'127.0.0.1','localhost','::1'}:raise RuntimeError('This demo supports loopback RPC only.')
    w=Web3(Web3.HTTPProvider(rpc,request_kwargs={'timeout':3}))
    if not w.is_connected():raise RuntimeError('Local Ethereum node is offline. Run npm run chain.')
    if w.eth.chain_id!=1337:raise RuntimeError('Expected development chain 1337; refusing transactions on another network.')
    artifact=json.loads((ROOT/'blockchain/ProductPassport.json').read_text())
    deployment=json.loads((ROOT/'.local/deployment.json').read_text())
    address=Web3.to_checksum_address(deployment['address'])
    if not w.eth.get_code(address):raise RuntimeError('No contract at the saved address. Run python scripts/deploy.py.')
    if Web3.to_hex(Web3.keccak(w.eth.get_code(address))) != deployment['code_hash']:raise RuntimeError('Contract code does not match this deployment record.')
    return w,w.eth.contract(address=address,abi=artifact['abi'])

def product_id(value):
    value=value.strip()
    if len(value)==66 and value.startswith('0x'):
        try:return bytes.fromhex(value[2:])
        except ValueError:raise ValueError('Invalid product ID')
    if not value:raise ValueError('Enter a product reference or ID')
    return bytes(Web3.keccak(text=value.upper()))

def send(w,fn,actor):
    # Explicitly restricted to a local node with unlocked development accounts.
    tx=fn.transact({'from':actor})
    receipt=w.eth.wait_for_transaction_receipt(tx,timeout=30)
    if receipt.status!=1:raise RuntimeError('Transaction reverted')
    return Web3.to_hex(tx),receipt.blockNumber
