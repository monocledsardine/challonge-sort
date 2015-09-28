# bracket.py
import collections
import math
import copy

class bracketRound(object):
    """Structural information for a round of a bracket."""

    def __init__(self, participants, round):
        """Create a specified round for a bracket with a certain number
        of participants.
        
        """    
        self._round = round
        self._participants = participants
        
        size = 1
        while size < self._participants:
            size *= 2
            
        self._roundSize = size / (2**(self._round-1))
        
    def __len__(self):
        return self._participants
        
    def min_rank(self):
        """Return the minimum rank of an element in this round, assuming
        standard, incremental ranking and a seeded bracket.
        
        """        
        if self._round == 1:
            return self._roundSize - self._participants + 1
        
        if self._round == 2:
            return min(1, self._roundSize*2 - self._participants)
        
        if self._round < 1:
            return self._roundSize//2 + 1
            
        return 0
        
    def max_rank(self):
        """Return the maximum rank of an element in this round, assuming
        standard, incremental ranking and a seeded bracket.
        
        """
        if self._round == 2:
            return max(0, self._roundSize*2 - self._participants)

        if self._round < 2:
            return self._roundSize
            
        return 0
    
    def row_size(self):
        return self._roundSize
        
    def shift(self, offset):
        """Shift the round up or down by the given offset."""
        self._roundSize = self._roundSize / 2**offset
        self._round += offset
        
        return self

class branchedElement(collections.Container):
    """A member of a bracket which contains two child members"""
    
    def __init__(self, first, second):
        """Create a single element of a bracket.
        
        >>> b = branchedElement(b1, b2)          # a element with child members b1 and b2 
        
        """
        self._rank = 0
        self._members = [copy.deepcopy(first), copy.deepcopy(second)]
        self.rank()
        
    def __getitem__(self, index):
        return self._members[index]

    def __setitem__(self, index, value):
        self._members[index] = copy.deepcopy(value)
        
    def __delitem__(self, index):
        del self._members[index]
        
    def __len__(self):
        return len(self._members)
        
    def __contains__(self, value):
        return value in self._members
    
    def _rank_member(self, m):
        if isinstance(m, branchedElement) or isinstance(m, rankedElement):
            return m.rank()
        
        return 0
    
    def rank(self):
        """Return the lowest rank number of an element's members. If there
        are no members, 0 is returned.
        
        """
        if len(self._members) > 0:
            self._rank = min([self._rank_member(x) for x in self._members])
        return self._rank
        
    def sum_members(self):
        """Return the sum of ranks of all members."""
        return sum([self._rank_member(x) for x in self._members])
    
    def _count_member(self, m):
        if isinstance(m, branchedElement) or isinstance(m, rankedElement):
            return m.count()
        
        return 0    
        
    def count(self):
        """Count the number of elements contained in this one and return it.
        Note that this element is included in the count as well as all sub-members.
        
        Because each element has either two or zero branches, the count is a
        unique, one-to-one integer representation of the shape of the tree beneath
        this element (proof: exercise for the reader). If you want to check that two 
        elements have the same tree structure, you can do so using the following check:
        
        >>> if element1.count() == element2.count():    #if they have the same structure...
        >>>     #do stuff...
        
        Alternatively, use element1.compare_structure(element2)
        """
        self._count = sum([self._count_member(x) for x in self._members]) + 1
        return self._count
        
    def compare_structure(self, other):
        """Return true if the branching structure of this element is equal to 
        that of other. Returns false otherwise."""
        
        return self.count() == other.count()        
        
    def residual(self, round):
        """Return the difference between the sum of ranks of this element's members and the
        average sum of ranks for pairs in a given round. A residual of zero implies that the 
        element is well-seeded in this round.
        
        round:  The bracketRound in which this element is contained

        """
        return (self.sum_members()-1-round.round_size())
        
        
class rankedElement(object):
    """A ranked singleton member of a bracket."""
    
    def __init__(self, rank=0):
        """Create a single element of a bracket with the specified rank"""
        self._rank = rank   
    
    def rank(self):
        """Return the rank of this element."""
        return self._rank
        
    
    def count(self):
        """Count the number of elements contained in this one - i.e., 1."""
        return 1
        
    def compare_structure(self, other):
        """Return true if the branching structure of this element is equal to 
        that of other. Returns false otherwise."""
        
        return self.count() == other.count()
        
    def residual(self, round):
        """Return the difference between this element's rank and the closest rank in the same
        round, given that both are seeded in the same round. A residual of zero implies that the 
        element is well-seeded in this round.
        
        round:  The bracketRound in which this element is contained

        """
        min_rank = round.min_rank()
        max_rank = round.max_rank()
        
        if self._rank < min_rank:
            return self._rank - min_rank
        
        if self._rank > max_rank:
            return self._rank - max_rank
        
        return 0
        
class RoundIter(object):
    """Iterates through a single row, or round, of a bracket"""
    def __init__(self):
        pass
        
    def __iter__(self):
        return self
        
    def next(self):
        pass 