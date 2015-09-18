import unittest
from views.datastorelogic import checkBooleanProperty

class TestDataStoreLogic(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_chekBooleanProperty_true_string(self):
        self.assertEqual(checkBooleanProperty('testfield', 'true'), True)
        
    def test_chekBooleanProperty_false_string(self):
        self.assertEqual(checkBooleanProperty('testfield', 'false'), False)
    
    def test_chekBooleanProperty_random_string(self):
        self.assertRaises(Exception, checkBooleanProperty, 'testfield', 'abc')
        
    def test_chekBooleanProperty_number(self):
        self.assertRaises(Exception, checkBooleanProperty, 'testfield', 0)