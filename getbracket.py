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

    r = requests.get('https://api.challonge.com/v1/tournaments/' + tournament + '/participants.xml', auth=(user, apikey))

    fname = tournament + '-participants.xml'
    output = open(fname, 'w')
    output.write(r.text)
    output.close()

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
    phase = 0
    m_temp = None
    for m in root.iter('match'):
        # Run the gamut of avaiable matches checks
        if int(m.find('round').text) <= phase:
            continue
        
        phase = int(m.find('round').text)
        m_temp = m
    
    for m in root.iter('match'):
        if phase-1 == int(m.find('round').text):
            return m
    
    return None
    
def generate(matchfile, participantfile=''):
    """ Generate a bracket from a file of matches.
    
    @matchfile: The location of the XML file containing match information 
    @playerfile: The location of the XML file containing player information
    
    """
    tourney = ET.parse(matchfile)
    root = tourney.getroot()    
    participants = ET.parse(participantfile).getroot()
    be = generate_branch(_find_top_match(root), root, participants)
    return bracket.bracket(be)
   
def generate_participant(id, participants):
    """ Generate a participant in the tournament as a rankedElement

    @id: the number used to identify the participant in the XML file
    @participants: the root for the element tree containing all participants
    
    """
    
    for p in participants.iter("participant"):
        for element in p.iter("id"):
            if element.text == id:
                return bracket.rankedElement(p.find("name").text, int(p.find("seed").text))
    
    raise ValueError("The player with ID " + id + " was not found.")

def generate_branch(match, root, participants):
    matchref = match.find('player1-prereq-match-id')
    
    if matchref.get('nil') != 'true':
        member1 = generate_branch(_find_match(root, matchref.text), root, participants)
    else:
        member1 = generate_participant(match.find('player1-id').text, participants)
    
    matchref = match.find('player2-prereq-match-id')
    if matchref.get('nil') != 'true':
        member2 = generate_branch(_find_match(root, matchref.text), root, participants)
    else:
        member2 = generate_participant(match.find('player2-id').text, participants)
        
    return bracket.branchedElement(member1, member2)