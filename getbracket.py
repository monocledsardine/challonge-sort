import sys
import httplib
import requests
import tree
import xml.etree.ElementTree as ET

'''if len(sys.argv) <= 2:
    print 'Gets the bracket from the challonge server.\n'
    print 'Example Usage: getbracket.py username api-key'
else:'''
#output = open('matches.xml', 'w')

def save_xml(tournament, user='Rococo', apikey='cKA7Mz88G2Kv1FEr2b25r0e3mrsJ4h1OcmJUAM1R'):
    r = requests.get('https://api.challonge.com/v1/tournaments/' + tournament + '/matches.xml', auth=(user, apikey))

    fname = tournament + '-matches.xml'
    output = open(fname, 'w')
    output.write(r.text)
    output.close()
    
    return fname
    
def find_match(root, matchid):
    for m in root.iter('match'):
        id = m.find('id').text
        
        if id == matchid:
            return m
            
def find_top_match(root):
    round = 0
    m_temp = None
    for m in root.iter('match'):
        # Run the gamut of avaiable matches checks
        if int(m.find('round').text) <= round:
            continue
        
        round = int(m.find('round').text)
        m_temp = m
    
    for m in root.iter('match'):
        if round-1 == int(m.find('round').text):
            return m
    
    return None
    
# Generate a bracket tree from an import XML file of matches
def generate_tree(matchfile):
    root = ET.parse(matchfile).getroot()
    
    myTree = tree.Tree([], 1)
    
    
    leaf_count = [0]
    
    def new_leaf(t):
        leaf_count[0] = leaf_count[0]+1
        l = tree.Leaf(str(leaf_count[0]), leaf_count[0])        
        t.leaves.append(l)
         
        return l
            
    def generate_branchpair(match):
        round = int(match.find('round').text)
        
        m1 = match.find('player1-prereq-match-id')
        if m1.get('nil') == 'true':
            m1 = None
             
        if m1 != None:
            m1_root = find_match(root, m1.text)
            member1 = generate_branchpair(m1_root)
        else:
            member1 = new_leaf(myTree)
        
        m2 = match.find('player2-prereq-match-id')
        if m2.get('nil') == 'true':
            m2 = None
        
        if m2 != None:
            m2_root = find_match(root, m2.text)
            member2 = generate_branchpair(m2_root)
        else:
            member2 = new_leaf(myTree)
            
        return myTree.add_branchpair(tree.Branch(member1, round), tree.Branch(member2, round))

    generate_branchpair(find_top_match(root))
   
    return myTree