import unittest
from urllib.parse import urlsplit,parse_qs
from passport_links import passport_url,qr_png

class PassportLinkTests(unittest.TestCase):
 def test_preserves_base_path_and_identifies_deployment(self):
  url=passport_url('https://example.test/passport?view=read','0x123',1337,'0xabc')
  p=urlsplit(url);q=parse_qs(p.query)
  self.assertEqual(p.path,'/passport');self.assertEqual(q['product'],['0x123']);self.assertEqual(q['chain'],['1337']);self.assertEqual(q['contract'],['0xabc']);self.assertEqual(q['view'],['read'])
 def test_invalid_destination_rejected(self):
  with self.assertRaises(ValueError):passport_url('localhost:8501','x',1337,'y')
 def test_qr_has_png_signature(self):
  self.assertTrue(qr_png('https://example.test').startswith(b'\x89PNG\r\n\x1a\n'))
