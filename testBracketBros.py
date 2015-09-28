# testBracketBros.py
import tree
import sys
import os
import random
import unittest
import bracketize
import getbracket

class bracketizeTestCase(unittest.TestCase):
    def test_load_players(self):
        testL = bracketize.load_players('player_data.xml')
        for x in testL:
            print x, x.rank(), x.tags
            
        t = tree.Tree(testL)
        tree.sort_tree(t)
        print(t)

def make_leaves(size):
    return [tree.Leaf(str(x), x) for x in range(1,size+1)]
    
class TreeTestCase(unittest.TestCase):
    def test_num_byes(self):
        self.assertEqual(tree.num_byes(2), 0)
        self.assertEqual(tree.num_byes(20), 12)
        self.assertEqual(tree.num_byes(33), 31)
        self.assertEqual(tree.num_byes(0.5), 0)
        self.assertEqual(tree.num_byes(3), 1)
        self.assertEqual(tree.num_byes(4), 0)
        self.assertEqual(tree.num_byes(5), 3)
        self.assertEqual(tree.num_byes(7), 1)
        
    def test_num_end_branches(self):
        self.assertEqual(tree.num_end_branches(2), 1)
        self.assertEqual(tree.num_end_branches(20), 4)
        self.assertEqual(tree.num_end_branches(33), 1)
        self.assertEqual(tree.num_end_branches(0.5), 0)
        self.assertEqual(tree.num_end_branches(3), 1)
        self.assertEqual(tree.num_end_branches(4), 2)
        self.assertEqual(tree.num_end_branches(5), 1)
        self.assertEqual(tree.num_end_branches(7), 3)
        
    def test_num_end_leaves(self):
        self.assertEqual(tree.num_end_leaves(2), 2)
        self.assertEqual(tree.num_end_leaves(20), 8)
        self.assertEqual(tree.num_end_leaves(33), 2)
        self.assertEqual(tree.num_end_leaves(0.5), 0)
        self.assertEqual(tree.num_end_leaves(3), 2)
        self.assertEqual(tree.num_end_leaves(4), 4)
        self.assertEqual(tree.num_end_leaves(5), 2)
        self.assertEqual(tree.num_end_leaves(7), 6)
    
    def test_num_rounds(self):
        self.assertEqual(tree.num_rounds(2), 1)
        self.assertEqual(tree.num_rounds(20), 5)
        self.assertEqual(tree.num_rounds(33), 6)
        self.assertEqual(tree.num_rounds(0.5), 0)
        self.assertEqual(tree.num_rounds(3), 2)
        self.assertEqual(tree.num_rounds(4), 2)
        self.assertEqual(tree.num_rounds(5), 3)
        self.assertEqual(tree.num_rounds(7), 3)
        
    def test_tree(self):
        n = random.randint(2, 16)
        leaves = make_leaves(n)
        treebeard = tree.Tree(leaves)
        self.assertEqual(len(treebeard.leaves), n)
        
        
        # count the number of branchpairs in each round
        round_count = []
        for x in range(1, tree.num_rounds(n)):
            round_count.append(0)
            for y in treebeard.branchpairs:
                round_count[x-1] += (y.round_number == x)
            
            if x < tree.num_rounds(n):
                self.assertEqual(round_count[x-1], 2**(x-1))
            else:
                self.assertEqual(round_count[x-1], tree.num_end_branches(n)//2)
        
        n1 = random.randint(2, 10)
        n2 = random.randint(2, 10)
        r = random.randint(1, 6)
        bp = treebeard.add_branchpair(
            tree.Branch(tree.Leaf(str(n1), n1), r), 
            tree.Branch(tree.Leaf(str(n2), n2), r))
        self.assertEqual(bp.rank(), min(n1, n2))
        self.assertEqual(bp.get_quality(), n1 + n2 - 2**r - 1)        
        
class treeTestCase(unittest.TestCase):
    def test_sort_tree(self):
        n = random.randint(2,33)
        
        ent = tree.Tree(make_leaves(n))
        print("Before sort:")
        ent.print_verbose()
        
        tree.sort_tree(ent)
        print("After sort:")
        ent.print_verbose()
        
        # Make sure that a sort with no restrictions and traditional seeding has all quality = 0
        for x in ent.branchpairs:
            self.assertEqual(x.get_quality(), 0)
            
        ent.print_ends()
        
    def test_sort_bad_seeds(self):
        leaves = [tree.Leaf("1", 1), tree.Leaf("2", 2),
            tree.Leaf("3", 3), tree.Leaf("4", 4),
            tree.Leaf("6a", 6), tree.Leaf("6b", 6),
            tree.Leaf("6c", 6)]
        pippin = tree.Tree(leaves)
        print("Before weird sort:")
        print(pippin)
        
        tree.sort_tree(pippin)
        print("After weird sort:")
        print(pippin)
        
        pippin.print_ends()

class getbracketTestCase(unittest.TestCase):
    def test_generate(self):
        t = tree.Tree(bracketize.load_players('player_data.xml'))
        
        tname = 'foobar18'
        
        print "Saved " + getbracket.save_xml(tname)
        
        gimli = getbracket.generate_tree(tname + '-matches.xml')
        
        print "Gimli: " + str(len(gimli.leaves))
        print "t: " + str(len(t.leaves))
        
        gimli.print_verbose()
        
        for l in gimli.leaves:
            print l
        
        t.print_verbose()
        
        gimli.define_leaves(t.leaves)            
        
if __name__ == "__main__":
    unittest.main()