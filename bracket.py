# bracket.py
import collections
import math
from copy import copy
import sys

def _num_rounds(num_participants):
    rounds = 1
    i = 2
    while i < num_participants:
        i *= 2
        rounds += 1
    
    return rounds
    
class bracketRound(object):
    """Structural information for a round of a bracket."""
    def __init__(self, participants, round=0):
        """Create a specified round for a bracket with a certain number
        of participants.
        
        """    
        self._round = round
        self._participants = participants
        
        size = 1
        while size < self._participants:
            size *= 2
            
        self._roundSize = size / (2**(self._round))
        
    def particpants(self):
        return self._participants
        
    def min_rank(self):
        """Return the minimum rank of an element in this round, assuming
        standard, incremental ranking and a seeded bracket.
        
        """        
        if self._round == 0:
            return self._roundSize - self._participants + 1
        
        if self._round == 1:
            return min(1, self._roundSize*2 - self._participants)
        
        if self._round < 0:
            return self._roundSize//2 + 1
            
        return 0
        
    def max_rank(self):
        """Return the maximum rank of an element in this round, assuming
        standard, incremental ranking and a seeded bracket.
        
        """
        if self._round == 1:
            return max(0, self._roundSize*2 - self._participants)

        if self._round < 1:
            return self._roundSize
            
        return 0
    
    def round_size(self):
        return self._roundSize
        
    def shift(self, offset):
        """Shift the round up or down by the given offset."""
        self._roundSize = self._roundSize / 2**offset
        self._round += offset
        
        return self

class branchedElement(collections.Container):
    """A member of a bracket which contains two child members"""
    
    def __init__(self, first=None, second=None):
        """Create a single element of a bracket.
        
        >>> b = branchedElement(b1, b2)          # a element with child members b1 and b2 
        
        """
        self._rank = 0
        self._members = [first, second]
        self.round = round
        
    def __getitem__(self, index):
        return self._members[index]

    def __setitem__(self, index, value):
        self._members[index] = value
        
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
    
    def _count_ranked_member(self, m):
        if isinstance(m, branchedElement) or isinstance(m, rankedElement):
            return m.count_ranked()
    
    def count_ranked(self):
        """Count the number of singleton elements contained within this element or 
        within this element's members.
        
        """
        return sum([self._count_ranked_member(x) for x in self._members])
        
    def count(self):
        """Count the number of sub-elements contained in this element and return it.
        Note that this element is included in the count (so an element containing
        two singleton members, for example, will have a count of 3). If this element's 
        members have members, then those members are counted as well, and this recurses
        until all nested elements are counted.
        
        Because each element has either two or zero branches, the count is a unique, 
        one-to-one integer representation of the shape of the bracket tree beneath
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
        element is well-seeded in this round. A negative residual implies that this is element
        is being seeded lower than expected, and a positive residual implies that this element 
        is being seeded higher than expected.

        """
       
        return (self.sum_members()-1-round.round_size()*2)
        
    def swap(self, other):
        """ Swap this element with another branched element in the bracket. This swap is purely
        conceptual - the end result uses copies of the two involved elements. Swapping
        is a generally slow process despite the simplicity of the concept, so use this 
        sparingly."""
        
        if self in other or other in self:
            raise ValueError("Can't swap directly nested elements!")
            #TODO: restrict deeply nested elements
        
        member1 = copy(self[0])
        member2 = copy(self[1])
        
        self[0] = copy(other[0])
        self[1] = copy(other[1])
        
        other[0] = member1
        other[1] = member2
        
class rankedElement(object):
    """A ranked singleton member of a bracket."""
    
    def __init__(self, name="", rank=0, **kwargs):
        """Create a single, ranked element of a bracket"""
        self._rank = rank
        
        if name == "":
            self.name = str(rank)
        else:        
            self.name = name
            
        self.round = round
        self.tags = kwargs
        self._count = 1
    
    def __str__(self):
        return str(self.name)
    
    def rank(self):
        """Return the rank of this element."""
        return self._rank
        
    def set_rank(self, value):
        """ Set this element's rank."""
        self._rank = value
        
    def count_ranked(self):
        """ Return 1. This is used recursively by branchedElement to count the number of 
        ranked elements in a bracket tree.
        
        """
        return 1
    
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

        """
        min_rank = round.min_rank()
        max_rank = round.max_rank()
        
        if self._rank < min_rank:
            return self._rank - min_rank
        
        if self._rank > max_rank:
            return self._rank - max_rank
        
        return 0
        
    def swap(self, other):
        """ Swap this element with another ranked element in the bracket. This swap is purely
        conceptual - the end result is copies of the two involved elements.
        
        """
        temp_rank = self._rank
        temp_name = self.name
        temp_tags = copy(self.tags)
        
        self._rank = other._rank
        self.name = other.name
        self.tags = copy(other.tags)
        
        other._rank = temp_rank
        other.name = temp_name
        other.tags = temp_tags
        
def print_bracket(top):
    """ Print a string representation of a bracket to the standard output stream.
    
    @top: the uppermost printed element in the bracket

    """
    num_tabs=0
    num_participants=top.count_ranked()
    top.count()
    
    def stringify_branch(b, num_tabs):
 
    
        if isinstance(b, branchedElement):
            print_tabs(num_tabs)
            print "{"
            num_tabs += 1
            
            stringify_branch(b[0], num_tabs)            
            stringify_branch(b[1], num_tabs)
            
            num_tabs -= 1
            print_tabs(num_tabs)
            print '}' + str(b.residual(bracketRound(num_participants, _num_rounds(num_participants)-num_tabs)))
        else:
            print_tabs(num_tabs)
            print " " + str(b) + ": " + str(b.residual(bracketRound(num_participants, _num_rounds(num_participants)-num_tabs)))
            
    def print_tabs(num_tabs):
        for i in range(num_tabs):
                sys.stdout.write('...')
            
        sys.stdout.flush()
            
    stringify_branch(top, num_tabs)
    
def sort(top):
    """ Sort a bracket. This sort attempts to get the bracket as close as possible 
    to a typical, seeded elimination format tournament bracket, where the rank of each 
    element is applied as its seed.

    @top: the uppermost of the elements you wish to sort
    
    This is a very slow process due to the lack of restrictions on seed (or "rank") 
    values. As such, if you wish to sort a standard bracket with basic seeding, 
    use a different approach for maximum efficiency.
    
    """
    num_participants = top.count_ranked()
    top.count()
    round = bracketRound(num_participants)
    e_round = bracketRound(num_participants)
    
    def rate_swap(e1, e2, r2=None):
        # rate a swap between two elements
        if e1 == None or e2 == None:
            return 0
        
        if e1._count != e2._count:
            return 0
        
        r1 = e1.residual(round)
        if r2 == None:
            r2 = e2.residual(e_round)
        
        return abs(r1) + abs(r2) - abs(r1 - e1._rank + e2._rank) - abs(r2 - e2._rank + e1._rank)
    
    def audition_swap(t, e):
        #find a swap candidate under top for element e
        tryout = None
        max_rating = 0
    
        if rate_swap(t, e) > max_rating:
            return t
            
        if isinstance(t, branchedElement):
            round.shift(-1)
            tryout1 = audition_swap(t[0], e)
            tryout2 = audition_swap(t[1], e)

            rating1 = rate_swap(tryout1, e)
            rating2 = rate_swap(tryout2, e)
            
            if rating1 > max_rating:
                tryout = tryout1
                max_rating = rating1
            
            if rating2 > max_rating:
                tryout = tryout2
                max_rating = rating2
            
            round.shift(1)
        
        return tryout
        
    def actually_swap(e):
        if isinstance(e, branchedElement):
            e_round.shift(-1)
            actually_swap(e[0])
            actually_swap(e[1])
            e_round.shift(1)
            
        tryout = audition_swap(top, e)
        if rate_swap(tryout, e) > 0:
            e.swap(tryout)
            
    actually_swap(top)
    
class RoundIter(object):
    """Iterates through a single row, or round, of a bracket"""
    def __init__(self):
        pass
        
    def __iter__(self):
        return self
        
    def next(self):
        pass 