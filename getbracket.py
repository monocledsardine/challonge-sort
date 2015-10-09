import sys
import httplib
import requests
import bracket
import xml.etree.ElementTree as ET
import getpass

DEBUG = True

def save_xml(tournament):
    # TODO: Implement a more convenient authentication method
    user = raw_input("Username: ")
    apikey = getpass.getpass("API Key: ")

    r = requests.get('https://api.challonge.com/v1/tournaments/' + tournament + '/matches.xml', auth=(user, apikey))

    fname = tournament + '-matches.xml'
    output = open(fname, 'w')
    output.write(r.text)
    output.close()
    
    return fname

    
def _find_match(root, matchid):
    for m in root.iter('match'):
        id = m.find('id').text
        
        if id == matchid:
            return m
            
def _find_top_match(root):
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
    
def generate(matchfile):
    """ Generate a bracket from a file of matches.
    
    @matchfile: The location of XML file containing match information 
    
    """
    tourney = ET.parse(matchfile)
    root = tourney.getroot()    
    return generate_branch(_find_top_match(root), root)
   
def generate_player(name, rank=0):
    """ Generate a player as a rankedElement

    @name: the unique string used to identify the player
    @rank: the seeding of the player in the bracket
    
    """
    return bracket.rankedElement(name, rank)


def generate_branch(match, root):
    matchref = match.find('player1-prereq-match-id')
    
    if matchref.get('nil') != 'true':
        member1 = generate_branch(_find_match(root, matchref.text), root)
    else:
        member1 = generate_player(match.find('player1-id').text)
    
    matchref = match.find('player2-prereq-match-id')
    if matchref.get('nil') != 'true':
        member2 = generate_branch(_find_match(root, matchref.text), root)
    else:
        member2 = generate_player(match.find('player2-id').text)
        
    return bracket.branchedElement(member1, member2)