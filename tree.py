# tree.py
import math
import sys
import itertools

DEBUG_MODE = False

SORT_BY_QUALITY = 1

RANK_TYPE_SEED = 1
RANK_TYPE_GLICKO = 2
PRINT_BRANCHPAIR_QUALITY = True
PRINT_BRANCHPAIR_RANK = False

# Returns the number of rounds in an n-leaf tree
def num_rounds(n):
    i = 0
    while 2**i <= n-1:
        i += 1
        
    return i
    
# Returns the number of byes in an n-leaf tree
def num_byes(n):    
    i = 0
    while 2**i < n:
        i += 1
        
    return int(math.floor(2**(i)-n))

def is_power_of_2(n):
    i = 1
    while i < n:
        i *= 2
    
    return (i == n)
    
# Returns the number of branches in the last round    
def num_end_branches(n):    
    i = 0
    while 2**i < n:
        i += 1
        
    return int(math.floor(n-2**(i-1)))
        
# Returns the number of leaves in the last round    
def num_end_leaves(n):    
    i = 0
    while 2**i < n:
        i += 1
    
    return int(math.floor(2*n-2**(i)))

class Leaf:
        def __init__(self, name, rank, tags=set()):
            self.name = name
            self._rank = rank
            self.tags = tags
        
        def rank(self):
            return self._rank

        def __str__(self):
            return str(self.name)
    
# Represents a single slot which will be filled by a player
# at some point during the bracket
class Branch:
    # content: the match or player held by the slot. Must have a rank method
    def __init__(self, content=None, round_number=1, parent=None):
        self.content = content
        self.round_number = round_number
        self.parent = parent
        
    def rank(self):
        if self.content == None:
            raise NameError("Branch: branch with no content being called for rank()")
        else:
            return self.content.rank()
    
    # switch this branch out with another
    def switch(self, other):
        temp_parent = other.parent
        other.parent = self.parent
        self.parent = temp_parent
        
        temp_round = other.round_number
        other.round_number = self.round_number
        self.round_number = temp_round
        
        self.parent.switch_branch(self, other)
        other.parent.switch_branch(self, other)
    
    def iter_branches(self, round_number=0):
        # assume that round_number >= 0
        if (self.round_number > round_number or round_number == 0):
            return itertools.chain(x.iter() for x in self.branches)
    
        
    def __str__(self):
        return (str(self.content))
    
# Connects two branches. Rank() returns the higher rank of the two.
# parent: the Branch which this BranchPair leads to in the bracket tree
class BranchPair:           
    def __init__(self, branch1, branch2, round_number=1, parent=None):
        if branch1.round_number != branch2.round_number:
            print("Warning: branches with different round numbers are being intertwined")
        
        self.parent = parent
        self.branches = [branch1, branch2]
        self.round_number = round_number
        
    def rank(self):
        minimum = None
       
        if len(self.branches) <= 0:
            raise NameError("BranchPair: no branches, but rank() is called")
        for x in self.branches:
            if minimum == None:
                minimum = x.rank()
            elif minimum > x.rank():
                minimum = x.rank()
               
        if minimum == None:
            raise NameError("BranchPair: rank() returns None")
            
        return minimum
    
    def get_quality(self):
        if self.parent == None:
            round_number = 1
        else:
            round_number = 2**self.parent.round_number
            
        rank_sum = 0
        for x in self.branches:
            rank_sum += x.rank()

        return (- 2**self.round_number - 1 + rank_sum)
    
    def switch_branch(self, one, two):
        #TODO: Sort by index, not branch
        if one not in self.branches and two not in self.branches:
            raise NameError("BranchPair: switching out a branch not owned by this branchpair")
    
        has_one = self.branches.count(one) > 0
        has_two = self.branches.count(two) > 0
        
        if has_one and has_two:
            i_one = self.branches.index(one)
            i_two = self.branches.index(two)
        
            self.branches[i_one] = two
            self.branches[i_two] = one
        elif has_one:
            self.branches[self.branches.index(one)] = two
        elif has_two:
            self.branches[self.branches.index(two)] =  one
    
    def __str__(self):
        concat = "{"
        for x in self.branches:
            concat += str(x) + ", "

        concat = concat[:-2] + "}"
        if PRINT_BRANCHPAIR_QUALITY:
            concat += ": " + str(self.get_quality())
            
        if PRINT_BRANCHPAIR_RANK:
            concat += ": " + str(self.rank())
        return concat

class Tree:
    def __init__(self, leaves):        
        self.grow_branches(leaves)
        self.num_rounds = num_rounds(len(self.leaves))
    
        self.size = len(leaves)
        
    def grow_branches(self, leaves):
        self.branchpairs = []
        self.branches = []
        
        self.leaves = leaves[:]
        length = len(leaves)
        end_leaves = num_end_leaves(length)
        current_round = num_rounds(length) - 1
        
        for i in range(num_end_branches(length)):
            self.add_branchpair(Branch(leaves.pop(), current_round+1), Branch(leaves.pop(), current_round+1))
       
        temp_branches = []
    
        j = 2**current_round
        for x in leaves:
            temp_branches.append(Branch(x, current_round))
            j -= 1
        
        while j > 0:
            temp_branches.append(Branch(self.branchpairs[j-1], current_round))
            j -= 1
            
        for i in range(len(temp_branches)//2):
            self.add_branchpair(temp_branches[2*i], temp_branches[2*i+1])
        
        current_round -= 1
            
        j = num_end_branches(length)
        while j < len(self.branchpairs)-1:
            for i in range(2**(current_round-1)):
                self.add_branchpair(Branch(self.branchpairs[j], current_round), Branch(self.branchpairs[j+1], current_round))
                j += 2
            
            current_round -= 1
        
    def add_branchpair(self, branch1, branch2):
        if branch1.round_number != branch2.round_number:
            print("Warning: branches with different round numbers are being intertwined")
        
        self.branches.append(branch1)
        self.branches.append(branch2)
        
        bp = BranchPair(branch1, branch2, branch1.round_number)
        self.branchpairs.append(bp)
        branch1.parent = bp
        branch2.parent = bp
        
        if isinstance(branch1.content, BranchPair):
            branch1.content.parent = bp
        
        if isinstance(branch2.content, BranchPair):
            branch2.content.parent = bp

        return bp
            
    def get_parent(self):
        b = self.branchpairs[0]
        
        while b.parent != None:
            b = b.parent
        
        return b
    
    def iter_branches(self, round_number=0):
        # find the parent branchpair, and iterate recursively
        bparent = self.get_parent()
    
        while round_number < 0:
            round_number += num
            
        return bparent.iter_branches(round_number)
    
    def print_verbose(self):
        concat = "Leaves:\n" + str(len(self.leaves)) + "\n\nBranches:\n1\t2\t3\t4\t5\t6\n"
        
        for x in self.branches:
            for i in range(x.round_number-1):
                concat += "\t"
            concat += str(x) + "\n"
            
        concat += "\nBranchPairs:\n"
            
        x = self.branchpairs[0]
        while x.parent != None:
            x = x.parent
        concat += str(x) + "\n"
        
        print(concat)
    
    def print_ends(self):
        print("Printing ends:")
        for x in self.branches:
            if x.round_number == self.num_rounds-(not is_power_of_2(len(self.leaves))):
                print x
        
    def __str__(self):        
        x = self.branchpairs[0]
        while x.parent != None:
            x = x.parent
        return (str(x) + "\n")
        
def sort_tree(t, type=SORT_BY_QUALITY):
    if type==SORT_BY_QUALITY:
        
        if DEBUG_MODE:
            print("Starting sort...") 
            i = 0
        
        change_flag = 1
        while change_flag == 1:
            change_flag = 0
            branches = t.branches[:]   
            while len(branches) > 1:
                branch = branches.pop()
                rank = branch.rank()
                quality = branch.parent.get_quality()
                
                rating = 0
                candidate = None
                for x in branches:
                    if ((x.round_number == branch.round_number
                        or (isinstance(x.content, Leaf) and isinstance(branch.content, Leaf)))
                        and x.parent != branch.parent):

                        q2 = x.parent.get_quality()
                        r2 = x.rank()

                        temp_rating = abs(quality) + abs(q2) - abs(quality - rank + r2) - abs(q2 - r2 + rank)
                        if temp_rating > rating:
                            rating = temp_rating
                            candidate = x
                                
                if rating > 0:
                    branch.switch(candidate)
                    change_flag = 1
                    if DEBUG_MODE:
                        print("Switched branch " + str(x) + " with " + str(branch))
                        i += 1
                        
        if DEBUG_MODE:
            print("Number of switches: " + str(i))