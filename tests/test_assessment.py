import unittest
from assessment_engine import evaluate, PROFILES

class AssessmentTests(unittest.TestCase):
 def setUp(self):
  self.checks={n:'Pass' for n in PROFILES['Smartphone']}
 def test_non_operation_overrides_high_scores(self):
  self.assertEqual(evaluate('Smartphone',100,0,100,self.checks)['route'],'Repairability inspection')
 def test_hazard_has_highest_priority(self):
  self.assertEqual(evaluate('Smartphone',100,100,100,self.checks,True)['route'],'Specialist handling')
 def test_failed_check_prevents_reuse(self):
  self.checks['Touchscreen response']='Failed'
  self.assertEqual(evaluate('Smartphone',100,100,100,self.checks)['route'],'Repair required')
 def test_unchecked_device_is_incomplete(self):
  self.assertEqual(evaluate('Monitor',90,90,None,{'Display':'Not checked'})['route'],'Inspection incomplete')
 def test_no_battery_is_excluded_from_average(self):
  self.assertEqual(evaluate('Monitor',80,100,None,{'Display':'Pass'})['score'],90)

if __name__=='__main__':unittest.main()
