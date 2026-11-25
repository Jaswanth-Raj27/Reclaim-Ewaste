"""Integration checks against an isolated contract on the loopback development node."""
import json,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from web3 import Web3
w=Web3(Web3.HTTPProvider('http://127.0.0.1:8545'));assert w.eth.chain_id==1337
artifact=json.loads((Path(__file__).resolve().parents[1]/'blockchain/ProductPassport.json').read_text())
a,b,outsider=w.eth.accounts[:3]
r=w.eth.wait_for_transaction_receipt(w.eth.contract(abi=artifact['abi'],bytecode=artifact['bytecode']).constructor().transact({'from':a}))
c=w.eth.contract(address=r.contractAddress,abi=artifact['abi'])
pid=w.keccak(text='integration-'+str(uuid.uuid4()));empty=bytes(32);evidence=w.keccak(text='test-evidence')
def tx(fn,actor=a):
 r=w.eth.wait_for_transaction_receipt(fn.transact({'from':actor}));assert r.status==1
def rejects(fn,actor=a):
 try:fn.call({'from':actor})
 except Exception:return
 raise AssertionError('Unauthorized/invalid operation succeeded')
tx(c.functions.register(pid,'Test device','Laptop',evidence));assert c.functions.getProduct(pid).call()[2]==a
rejects(c.functions.register(pid,'Duplicate','Laptop',empty))
rejects(c.functions.updateStage(pid,1,'Collect',empty),outsider)
rejects(c.functions.updateStage(pid,4,'Skip to recycled',empty))
tx(c.functions.proposeTransfer(pid,b));assert c.functions.getProduct(pid).call()[2]==a
rejects(c.functions.acceptTransfer(pid),outsider)
rejects(c.functions.updateStage(pid,1,'During pending transfer',empty))
tx(c.functions.acceptTransfer(pid),b);assert c.functions.getProduct(pid).call()[2]==b
rejects(c.functions.appendNote(pid,'Old owner',empty),a)
for stage in [1,2,3,1,2,4]:tx(c.functions.updateStage(pid,stage,'Lifecycle test',empty),b)
rejects(c.functions.proposeTransfer(pid,a),b)
rejects(c.functions.updateStage(pid,1,'After recycled',empty),b)
before=c.functions.historyAt(pid,0).call();tx(c.functions.appendNote(pid,'Correction as new note',empty),b)
assert c.functions.historyAt(pid,0).call()==before
assert before[4]==evidence
pid2=w.keccak(text='cancel-'+str(uuid.uuid4()));tx(c.functions.register(pid2,'Cancel test','Monitor',empty));tx(c.functions.proposeTransfer(pid2,b));tx(c.functions.cancelTransfer(pid2));rejects(c.functions.acceptTransfer(pid2),b)
print('Blockchain integration passed: registration, duplicate prevention, permissions, two-party custody, cancellation, lifecycle order, terminal recycling, append-only correction and evidence hash.')
