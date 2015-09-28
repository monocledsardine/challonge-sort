# test.py
from bracket import bracketRound, branchedElement, rankedElement
import unittest

class TestRounds(unittest.TestCase):
    def test_basic_stuff(self):
        r1 = bracketRound(participants=10, round=1)
        
        self.assertEqual(r1.min_rank(), 7)
        self.assertEqual(r1.max_rank(), 16)
        
        r1.shift(1)
        
        self.assertEqual(r1.min_rank(), 1)
        self.assertEqual(r1.max_rank(), 6)
    
class TestElements(unittest.TestCase):
    def test_list_functions(self):
        # __init__
        b1 = branchedElement("one", "two")
        b1dupe = branchedElement(b1, b1)
        self.assertTrue(b1dupe[0] != b1dupe[1])
        
        # __getitem__
        b2 = branchedElement("hi", "there")
        self.assertEqual(b2[0], "hi")
        self.assertEqual(b2[1], "there")
        
        # __setitem__
        b2[0] = "hello"
        b2[1] = "world!"
        self.assertEqual(b2[0] + " " + b2[1], "hello world!")
        
        # __len__, __delitem__
        self.assertEqual(len(b2), 2)
        del b2[1]
        self.assertEqual(len(b2), 1)
        del b2[0]
        self.assertEqual(len(b2), 0)
        
        # __contains__
        b3 = branchedElement(rankedElement(4), rankedElement(4))
        b3first = b3[0]
        self.assertTrue(b3first in b3)
        self.assertFalse(rankedElement(4) in b3)
        
    def test_rank(self):
        # simple, ranked element
        b1 = rankedElement(10)
        self.assertEqual(b1.rank(), 10)
        
        # two ranked members
        b2 = branchedElement(rankedElement(4), rankedElement(8))
        self.assertEqual(b2[0].rank(), 4)
        self.assertEqual(b2[1].rank(), 8)
        self.assertEqual(b2.rank(), 4)
        
        # unranked memebers
        b3 = branchedElement(rankedElement(), rankedElement())
        self.assertEqual(b3.rank(), 0)
        
    def test_sum_members(self):
        b1 = branchedElement(rankedElement(8), rankedElement(2))
        self.assertEqual(b1.sum_members(), 10)
    
    def test_count(self):
        b1 = branchedElement(branchedElement(rankedElement(), rankedElement()), rankedElement())
        self.assertEqual(b1.count(), 5)

    def test_rate(self):
        b1 = rankedElement(1)
        b2 = rankedElement(2)
        b3 = rankedElement(7)
        b4 = rankedElement(16)
        
        b5 = branchedElement(b1, b2)
        b6 = branchedElement(b2, b3)
        b7 = branchedElement(b1, b4)
        
        r1 = bracketRound(participants=7, round=2)
        
        self.assertEqual(b1.residual(r1), 0)
        self.assertEqual(b1.residual(r1.shift(-1)), -1)
    
if __name__ == "__main__":
    unittest.main()