# test.py
from bracket import bracketRound, branchedElement, rankedElement, print_bracket
import bracket
import unittest
import getbracket

class TestRounds(unittest.TestCase):
    def test_basic_stuff(self):
        r1 = bracketRound(participants=10, round=0)
        
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
        #self.assertTrue(b1dupe[0] != b1dupe[1])
        
        b1 = branchedElement()
        self.assertEqual(len(b1), 2)
        self.assertEqual(b1.rank(), 0)
        
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
        b3 = branchedElement(rankedElement("four", 4), rankedElement("4", 4))
        b3first = b3[0]
        self.assertTrue(b3first in b3)
        self.assertFalse(rankedElement("bloop", 4) in b3)
        
    def test_rank(self):
        # simple, ranked element
        b1 = rankedElement("ten", 10)
        self.assertEqual(b1.rank(), 10)
        
        # two ranked members
        b2 = branchedElement(rankedElement("four", 4), rankedElement("eight", 8))
        self.assertEqual(b2[0].rank(), 4)
        self.assertEqual(b2[1].rank(), 8)
        self.assertEqual(b2.rank(), 4)
        
        # unranked memebers
        b3 = branchedElement(rankedElement(), rankedElement())
        self.assertEqual(b3.rank(), 0)
        
        b3[0].set_rank(5)
        b3[1].set_rank(4)
        
        self.assertEqual(b3.rank(), 4)
        
    def test_sum_members(self):
        b1 = branchedElement(rankedElement("eight", 8), rankedElement("two", 2))
        self.assertEqual(b1.sum_members(), 10)
    
    def test_count(self):
        b1 = branchedElement(branchedElement(rankedElement(), rankedElement()), rankedElement())
        self.assertEqual(b1.count(), 5)

    def test_residual(self):
        b1 = rankedElement(rank=1)
        b2 = rankedElement(rank=2)
        b3 = rankedElement(rank=7)
        b4 = rankedElement(rank=16)
        
        b5 = branchedElement(b1, b2)
        b6 = branchedElement(b2, b3)
        b7 = branchedElement(b1, b4)
        
        r1 = bracketRound(participants=7, round=1)
        
        self.assertEqual(b1.residual(r1), 0)
        self.assertEqual(b1.residual(r1.shift(-1)), -1)
        
        b8 = rankedElement(rank=6)
        b10 = rankedElement(rank=7)
        b9 = branchedElement(b8, b10)
        r2 = bracketRound(participants=8, round=1)
        
        self.assertEqual(b9.residual(r2), 4)
        self.assertEqual(b8.residual(r2.shift(-1)), 0)
        
    def test_swap(self):
        b1 = rankedElement("Charles", 1)
        b2 = rankedElement("Anakin", 2)
        b3 = rankedElement("George", 3)
        
        b4 = branchedElement(b1, b2)
        b5 = branchedElement(b3, b4)
                
        self.assertEqual(b5[0].rank(), 3) 
        self.assertEqual(b5[0].name, "George") 
        
        b1.swap(b3)
        
        self.assertEqual(b5[0].rank(), 1) 
        self.assertEqual(b5[0].name, "Charles") 
                
        self.assertEqual(b4[0].rank(), 3) 
        self.assertEqual(b4[0].name, "George")
        
        b5[0].swap(b4[0])
        
        self.assertEqual(b5[0].rank(), 3) 
        self.assertEqual(b5[0].name, "George")

        self.assertEqual(b4[0].rank(), 1) 
        self.assertEqual(b4[0].name, "Charles")
        
        with self.assertRaises(ValueError):
            b5.swap(b4)
        
        b6 = rankedElement("Errol", 4)
        b7 = rankedElement("Hedwig", 5)
        
        b8 = branchedElement(b6, b7)
        
        b8.swap(b4)
        
        self.assertEqual(b4.rank(), 4)
        self.assertEqual(b8.rank(), 1)
        
        b9 = branchedElement(b3, branchedElement(b1, b2))
        b9.swap(b4)
        
        self.assertEqual(b9.count(), 3)
        self.assertEqual(b4.count(), 5)
        
class TestGetBracket(unittest.TestCase):
    '''def test_getbracket(self):
        name = "foobar-18"
        fullname = "foobar18-matches.xml"
        getbracket.save_xml(name)
    
        be = getbracket.generate(fullname)
        
        if getbracket.DEBUG:
            print_bracket(be)
        
        self.assertEqual(len(be), 2)
        self.assertEqual(be.count(), 29)
        self.assertEqual(be.count_ranked(), 15)'''
        
    def test_sort(self):
        getbracket.save_xml("foobar18")
        
        be = getbracket.generate("foobar18-matches.xml", "foobar18-participants.xml")
               
        bracket.sort(be)
        
        if getbracket.DEBUG:
            print_bracket(be)
        
if __name__ == "__main__":
    unittest.main()