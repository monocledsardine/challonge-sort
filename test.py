# test.py
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bracket
from bracket import bracketPhase, branchedElement, rankedElement
import unittest
import getbracket
import random

class TestPhases(unittest.TestCase):
    def test_basic_stuff(self):
        r1 = bracketPhase(participants=10, phase=0)
        
        self.assertEqual(r1.min_rank(), 7)
        self.assertEqual(r1.max_rank(), 16)
        
        r1 = r1.shifted(1)
        
        self.assertEqual(r1.min_rank(), 1)
        self.assertEqual(r1.max_rank(), 6)
        
        r2 = bracketPhase(participants=4).shifted_to_top()
        self.assertEqual(r2.size(), 1)
        self.assertEqual(r2.min_rank(), 0)
        self.assertEqual(r2.max_rank(), 0)
        
        r2 = r2.shifted(-2)
        self.assertEqual(r2.min_rank(), 1)
        self.assertEqual(r2.max_rank(), 4)
    
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

    def test_phase(self):
        b1 = rankedElement(rank=1)
        b2 = rankedElement(rank=2)
        
        self.assertEqual(b1.phase.size(), 1)
        self.assertEqual(b2.phase.size(), 1)
        
        b3 = branchedElement(b1, b2)
        
        self.assertEqual(b1.phase.size(), 1)
        self.assertEqual(b2.phase.size(), 1)
        
        self.assertEqual(b3.phase, None)
        
        b3.phase = bracketPhase(2).shifted_to_top()
        
        self.assertEqual(b1.phase.size(), 2)
        self.assertEqual(b2.phase.size(), 2)
        self.assertEqual(b3.phase.size(), 1)
        self.assertEqual(b1.phase, b2.phase)
        
    def test_residual(self):
        b1 = rankedElement(rank=1)
        b2 = rankedElement(rank=2)
        b3 = rankedElement(rank=7)
        b4 = rankedElement(rank=16)
        
        b5 = branchedElement(b1, b2)
        b6 = branchedElement(b3, b4)
        
        r1 = bracketPhase(participants=4).shifted_to_top()
        b7 = branchedElement(b5, b6, r1)
        
        self.assertEqual(b1.residual(), 0)
        self.assertEqual(b2.residual(), 0)
        self.assertEqual(b3.residual(), 3)
        self.assertEqual(b4.residual(), 12)
        self.assertEqual(b5.residual(), -2)
        self.assertEqual(b6.residual(), 18)
        self.assertEqual(b7.residual(), 5)
        
        b8 = rankedElement(rank=6)
        b9 = rankedElement(rank=7)
        
        b10 = branchedElement(b8, b9)
        
        r2 = bracketPhase(participants=6).shifted_to_top()
        b11 = branchedElement(b7, b10, r2)
        
        self.assertEqual(b1.residual(), -2)
        self.assertEqual(b2.residual(), -1)
        self.assertEqual(b3.residual(), 0)
        self.assertEqual(b4.residual(), 8)
        self.assertEqual(b5.residual(), -6)
        self.assertEqual(b6.residual(), 14)
        self.assertEqual(b7.residual(), 3)
        self.assertEqual(b8.residual(), 4)
        self.assertEqual(b9.residual(), 5)
        self.assertEqual(b10.residual(), 8)
        self.assertEqual(b11.residual(), 4)
        
    def test_phase(self):
        b1 = rankedElement()
        b2 = rankedElement()
        b3 = rankedElement()
        b4 = branchedElement(b1, b2)
        b5 = branchedElement(b3, b4)
        
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
        
    def test_iter(self):
        composers = ["Ludwig", "Copland", "Bernstein", "Britten", "Schubert", "Chopin"]
    
        b1 = rankedElement(composers[0])
        b2 = rankedElement(composers[1])
        b3 = rankedElement(composers[2])
        b4 = rankedElement(composers[3])
        b5 = rankedElement(composers[4])
        b6 = rankedElement(composers[5])
        b7 = branchedElement(b1, b2)
        b8 = branchedElement(b3, b4)
        
        b9 = branchedElement(b5, b7)
        b10 = branchedElement(b6, b8)
        
        top = branchedElement(b9, b10)
        
        br = bracket.bracket(top)
        
        elements = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, top]
        
        for e in br:
            if e in elements:
                elements.remove(e)
            else:
                raise ValueError("Found element " + str(e) + " in this tree for some reason!")
                
        self.assertEqual(len(elements), 0)
        
class TestBracket(unittest.TestCase):
    def generate_bracket(self, num):
        participants = []
        for i in range(num):
            participants.append(rankedElement(str(i), i))
        
        random.shuffle(participants)
    
    def get_bracket(self):
        return getbracket.generate("foobar18-matches.xml", "foobar18-participants.xml")
        
    def test_print(self):
        b = self.get_bracket()
        
        #print_bracket(b)
    
    def test_sort(self):
        b = self.get_bracket()
        
        counts = {1:[], 3:[], 5:[], 7:[], 13:[], 15:[], 29:[]}
        for e in b:
            counts[e._count].append(e)
        
        ranks = {}
        for e in counts[1]:
            ranks[e._rank] = e
        
        self.assertEqual(b._rate_swap(counts[7][0][0], counts[7][0], counts[3][1][0], counts[3][1]), 0)
        
        if bracket.DEBUG:
            print "---------------------- BEFORE SORT ----------------------"
            b.print_verbose()
        
        b.sort()
            
        if bracket.DEBUG:
            print "---------------------- AFTER  SORT ----------------------"
            b.print_verbose()
        
        for e in b:
            self.assertEqual(e.residual(), 0)
        
    def test_iter_phase(self):
        b = self.get_bracket()
        
        f = b.iter_phase(0)
        g = b.iter_phase(1)
        
        ranked_elements = [i.rank() for i in g]
        ranked_elements += [i.rank() for i in f]
        
        self.assertEqual(ranked_elements, [12,8,9,4,6,3,1,2,15,7,10,5,14,13,11])
    
    def test_really_big_sort(self):
        #print "Testing really big sort..."
        
        self.generate_bracket(1000)

    def test_post(self):
        #b = self.get_bracket()
        #getbracket.post_bracket(b, "foobar19")
        pass
        
if __name__ == "__main__":
    unittest.main()