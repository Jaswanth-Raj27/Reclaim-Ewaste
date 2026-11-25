import unittest
from types import SimpleNamespace
from chain_explorer import mine_development_block

class MiningTests(unittest.TestCase):
 def test_refuses_other_networks(self):
  with self.assertRaisesRegex(RuntimeError,'restricted'):
   mine_development_block(SimpleNamespace(eth=SimpleNamespace(chain_id=1)))
 def test_surfaces_rpc_error(self):
  w=SimpleNamespace(eth=SimpleNamespace(chain_id=1337,block_number=3),provider=SimpleNamespace(make_request=lambda *_:{'error':{'message':'node rejected'}}))
  with self.assertRaisesRegex(RuntimeError,'node rejected'):mine_development_block(w)
 def test_requires_new_confirmed_block(self):
  w=SimpleNamespace(eth=SimpleNamespace(chain_id=1337,block_number=3,get_block=lambda _:SimpleNamespace(number=3)),provider=SimpleNamespace(make_request=lambda *_:{'result':'0x0'}))
  with self.assertRaisesRegex(RuntimeError,'No new block'):mine_development_block(w)
