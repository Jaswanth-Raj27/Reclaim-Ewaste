import unittest
from types import SimpleNamespace
from chain_explorer import verify_chain

class ChainVerificationTests(unittest.TestCase):
    def node(self,broken=False):
        blocks=[SimpleNamespace(hash=bytes([i]),parentHash=bytes([i-1]) if i else b'') for i in range(4)]
        if broken:blocks[2].parentHash=b'wrong'
        return SimpleNamespace(eth=SimpleNamespace(block_number=3,get_block=lambda n:blocks[n]))
    def test_checks_all_links(self):self.assertEqual(verify_chain(self.node()),3)
    def test_rejects_broken_middle_link(self):
        with self.assertRaisesRegex(ValueError,'Block #2'):verify_chain(self.node(True))
