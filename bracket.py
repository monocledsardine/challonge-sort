# bracket.py
import collections
import math
import copy
import sys
    
class bracketPhase(object):
    """Structural information for a phase of a bracket."""
    def __init__(self, participants, phase=0):
        """Create a specified phase for a bracket with a certain number
        of participants.
        
        """    
        if phase < 0:
            phases = 1
            i = 2
            while i < participants:
                i *= 2
                phases += 1
            
            self._phase = phases+phase
        else:
            self._phase = phase
        
        self._participants = participants
        
        size = 1
        while size < self._participants:
            size *= 2
            
        self._size = size / (2**(self._phase))
        
    def particpants(self):
        return self._participants
        
    def min_rank(self):
        """Return the minimum rank of an element in this phase, assuming
        standard, incremental ranking and a seeded bracket.
        
        """        
        if self._phase == 0:
            return self._size - self._participants + 1
        
        if self._phase == 1:
            return min(1, self._size*2 - self._participants)
        
        if self._phase < 0:
            return self._size//2 + 1
            
        return 0
        
    def max_rank(self):
        """Return the maximum rank of an element in this phase, assuming
        standard, incremental ranking and a seeded bracket.
        
        """
        if self._phase == 1:
            return max(0, self._size*2 - self._participants)

        if self._phase < 1:
            return self._size
            
        return 0
    
    def size(self):
        return self._size
        
    def shifted(self, offset):
        """Return a copy of this phase shifted by the given offset."""
        p = copy.deepcopy(self)
       
        p._size = p._size / (2**offset)
        p._phase += offset
        
        return p
        
    def shifted_to_top(self):
        """Return a phase with size 1 that is otherwise the same as this phase."""
        return self.shifted(math.floor(math.log(self._size, 2)))

class branchedElement(collections.Container):
    """A member of a bracket which contains two child members"""
    
    def __init__(self, first=None, second=None, phase=None):
        """Create a single element of a bracket.
        
        >>> b = branchedElement(b1, b2)          # a element with child members b1 and b2 
        
        """
        self._rank = 0
        self._members = [first, second]
        if phase != None:
            self.phase = phase
        else:
            self._phase = phase
        
    def __iter__(self):
        """ Return a generator for all the items contained in this element (including itself)"""
        yield self
        
        for i in self[0]:
            yield i
        for j in self[1]:
            yield j
        
    def __getitem__(self, index):
        return self._members[index]

    def __setitem__(self, index, value):
        self._members[index] = value
        phase = self._phase
        
    def __delitem__(self, index):
        del self._members[index]
        
    def __len__(self):
        return len(self._members)
        
    def __contains__(self, element):
        # TODO: Fix this so that all elements that get caught
        # by the iterator are also caught here. Refactor the code 
        # so that contains_elements is no longer used and this is
        # used instead.
        return element in self._members
    
    @property
    def phase(self):
        return self._phase
        
    @phase.setter
    def phase(self, p):
        self._phase = p
        
        plowered = p.shifted(-1)
        self[0].phase = plowered
        self[1].phase = plowered
    
    def contains_element(self, element):
        if element in self:
            return true
        
        element_in_submembers = False
        if isinstance(self[0], branchedElement):
            if self[0].contains_element(element):
                element_in_submembers = True
        
        if isinstance(self[1], branchedElement):
            if self[1].contains_element(element):
                element_in_submembers = True
        
        return element_in_submembers
    
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
        
        Because each element has either two or zero branches, and the number of phases
        which rankedElements are removed from each other is at most 1, the count is a unique, 
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
        
    def residual(self):
        """Return the difference between the sum of ranks of this element's members and the
        average sum of ranks for pairs in a given phase. A residual of zero implies that the 
        element is well-seeded in this phase. A negative residual implies that this is element
        is being seeded lower than expected, and a positive residual implies that this element 
        is being seeded higher than expected.

        """
       
        return (self.sum_members()-1-self.phase.size()*2)
        
    def swap(self, other):
        """ Swap this element with another branched element in the bracket. This swap is purely
        conceptual - the members are swapped rather than the actual elements.
        
        """
        
        if self in other or other in self:
            raise ValueError("Can't swap directly nested elements!")
            #TODO: restrict deeply nested elements
        
        member1 = self[0]
        member2 = self[1]
        
        self[0] = other[0]
        self[1] = other[1]
        
        other[0] = member1
        other[1] = member2
        
class rankedElement(object):
    """A ranked singleton member of a bracket."""
    
    def __init__(self, name="", rank=0, phase=None, **kwargs):
        """Create a single, ranked element of a bracket"""
        self._rank = rank
        
        if name == "":
            self.name = str(rank)
        else:        
            self.name = name
        
        if phase == None:
            self.phase = bracketPhase(1)
        else:
            self.phase = phase
        
        self.tags = kwargs
        self._count = 1
    
    def __iter__(self):
        """ Returns this element. Helps the iteration process through a bracket."""
        yield self
    
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
        
    def residual(self):
        """Return the difference between this element's rank and the closest rank in the same
        phase, given that both are seeded in the same phase. A residual of zero implies that the 
        element is well-seeded in this phase.

        """
        min_rank = self.phase.min_rank()
        max_rank = self.phase.max_rank()
        
        if self._rank < min_rank:
            return self._rank - min_rank
        
        if self._rank > max_rank:
            return self._rank - max_rank
        
        return 0
    
    def swap(self, other):
        """ Swap this element with another ranked element in the bracket. This swap is purely
        conceptual - the data from each element is swapped.
        
        """
        temp_rank = self._rank
        temp_name = self.name
        temp_tags = copy.copy(self.tags)
        
        self._rank = other._rank
        self.name = other.name
        self.tags = copy.copy(other.tags)
        
        other._rank = temp_rank
        other.name = temp_name
        other.tags = temp_tags
    
class bracket(collections.Container):
    """A binary tree of elements that can be sorted by rank into a standard
    tournament bracket format."""
    
    def __init__(self, top):
        """Generate a bracket from a bracket element. This automatically creates
        phase information based on the sub-elements contained in the top element.
        
        @top: the topmost element in the bracket
        
        """
        self.top = top
        self._participants = top.count_ranked()
        self._phase = bracketPhase(self._participants).shifted_to_top()
        self.top.phase = self._phase
        
        # make sure everything is up to date
        top.rank()
        top.count()
    
    def __contains__(self, element):
        """Return true if the element is in this bracket tree."""
        return self.top.contains_element(element)
    
    def __iter__(self):
        for i in self.top:
            yield i
        
    def _rate_swap(self, a, apar, b, bpar):
        """Rate a swap between two elements from this bracket."""
        if a == b:
            return 0
    
        if a._count != b._count:
            return 0
        
        ra = apar.residual()
        rb = bpar.residual()
        
        return abs(ra) + abs(rb) - abs(ra - a._rank + b._rank) - abs(rb - b._rank + a._rank)
            
    def _find_swap_candidate(self, upper, e):
        """ Find a swap candidate under the upper element for the element e."""
        tryout = None
        max_rating = 0

        if self._rate_swap(upper, e) > max_rating:
            return upper
            
        if isinstance(upper, branchedElement):
            tryout1 = self._find_swap_candidate(upper[0], e)
            tryout2 = self._find_swap_candidate(upper[1], e)

            if tryout1 != None:
                rating1 = self._rate_swap(tryout1, e)
            
                if rating1 > max_rating:
                    tryout = tryout1
                    max_rating = rating1
            
            
            if tryout2 != None:
                rating2 = self._rate_swap(tryout2, e)
                
                if rating2 > max_rating:
                    tryout = tryout2
                    max_rating = rating2

        return tryout

    def _reposition(self, e):
        # Check if e is swappable with another element in the tree, 
        # and reposition it if so
        if isinstance(e, branchedElement):
            self._reposition(e[0])
            self._reposition(e[1])
            
        tryout = self._find_swap_candidate(self.top, e)
        if tryout != None:
            e.swap(tryout)
           
    def _get_rankeds(self):
        participles = []
        
        for e in self:
            if e._count in [3,5]:
                if e[0]._count == 1:
                    participles.append((e[0], e))
                if e[1]._count == 1:
                    participles.append((e[1], e))
        
        return participles
        
    def _get_branches(self):
        branches = []
        
        for e in self:
            if e._count not in [1,3]:
                if e[0]._count != 1:
                    branches.append((e[0], e))
                if e[1]._count != 1:
                    branches.append((e[1], e))
        
        return branches
    
    def _sort_elements(self, e_list):
        for (e, par) in e_list:
            max_rating = 0
            tryout = None
        
            if par.residual() != 0:
                for (e2, par2) in e_list:
                    rating = self._rate_swap(e, par, e2, par2)
                    if rating > max_rating:
                        max_rating = rating
                        tryout = e2
                
                if max_rating > 0:
                    e.swap(tryout)
                    return True
                    
        return False
        
        
    def sort(self):
        """ Sort this bracket. This sort attempts to get the bracket as close as possible 
        to a typical, seeded elimination format tournament bracket, where the rank of each 
        element is applied as its seed.

        This is a very slow process due to the lack of restrictions on rank values. 
        As such, if you wish to sort a standard bracket with basic seeding, use a 
        different approach for maximum efficiency.
        
        """
        while self._sort_elements(self._get_rankeds()):
            pass

        while self._sort_elements(self._get_branches()):
            pass
            
    def print_verbose(self):
        num_tabs=0
        num_participants=self._participants
        
        def stringify_branch(b, num_tabs):
            if isinstance(b, branchedElement):
                print_tabs(num_tabs)
                print "{"
                num_tabs += 1
                
                stringify_branch(b[0], num_tabs)            
                stringify_branch(b[1], num_tabs)
                
                num_tabs -= 1
                print_tabs(num_tabs)
                print '}' + str(b.residual())
            else:
                print_tabs(num_tabs)
                print " " + str(b._rank) + ": " + str(b.residual())
                
        def print_tabs(num_tabs):
            for i in range(num_tabs):
                    sys.stdout.write('...')
                
            sys.stdout.flush()
                
        stringify_branch(self.top, num_tabs)