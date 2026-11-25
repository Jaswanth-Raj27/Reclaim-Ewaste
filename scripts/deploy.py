import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from web3 import Web3
root=Path(__file__).resolve().parents[1]
w=Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if not w.is_connected() or w.eth.chain_id!=1337:raise SystemExit('Start the local development node first: npm run chain')
artifact=json.loads((root/'blockchain/ProductPassport.json').read_text())
record=root/'.local/deployment.json'
if record.exists():
 existing=json.loads(record.read_text());code=w.eth.get_code(existing['address'])
 if code and Web3.to_hex(Web3.keccak(code))==existing.get('code_hash'):print('Existing deployment:',existing['address']);raise SystemExit(0)
factory=w.eth.contract(abi=artifact['abi'],bytecode=artifact['bytecode'])
r=w.eth.wait_for_transaction_receipt(factory.constructor().transact({'from':w.eth.accounts[0]}))
assert r.status==1
record.parent.mkdir(exist_ok=True)
record.write_text(json.dumps({'address':r.contractAddress,'chain_id':1337,'block':r.blockNumber,'code_hash':Web3.to_hex(Web3.keccak(w.eth.get_code(r.contractAddress)))},indent=2))
print('Deployed ProductPassport:',r.contractAddress,'block:',r.blockNumber)
