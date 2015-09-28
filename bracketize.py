import sys
import math
import httplib
import requests
import challonge
import tree
import xml.etree.ElementTree as ET

# retrieve a list of players from an XML file
def load_players(fname):
    root = ET.parse(fname).getroot()
    
    leaves = []
    
    player_list = root.findall('player')
    
    lowest_rank = 0
    unranked_count = 0
    # find the number of unranked players
    for p in player_list:
        if p.find('rank') == None:
            unranked_count += 1
        else:
            lowest_rank = max(lowest_rank, int(p.find('rank').text))
    
    for p in root.iter('player'):
        name = p.get('name')
        tags = set()
        
        for t in p.iter('tag'):
            tags |= {t.get('name')}
        
        
        rank = p.find('rank')
        if rank == None:
            leaves.append(tree.Leaf(name, lowest_rank+(unranked_count+1.0)/2, tags))
        else:
            leaves.append(tree.Leaf(name, float(rank.text), tags))
    
    return leaves
    
def export_tree(tr):
    pass#for x in tr.iter_branches(round_number=-1)

    
class Bracket:
    def __init__(self, tree):
        self.members = []
        self.generate_from(tree)

    def generate_from(self, tree):
        #blindly populate all the edge members
        for x in tree.branches:
            if x.round_number == self.num_rounds-1-(not is_power_of_2(len(self.leaves))):
                for y in x:
                    members.append(y)