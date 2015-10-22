# getbracket.py
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

import sys
import httplib
import requests
import bracket
import xml.etree.ElementTree as ET
import getpass
import itertools
#TODO: Utilize existing REST API - pychallonge

DEBUG = True

def authorize():
    # TODO: Implement a more convenient authentication method
    user = raw_input("Username: ")
    apikey = getpass.getpass("API Key: ")

    return (user, apikey)

def post_bracket(b, tournament):
    """ POST a bracket object to challonge. There is no validation involved here.
    The bracket is sent as-is to challonge via bulk participant addition, which 
    may yield unexpected results due to challonge's limited bracket structures. 
    POST with caution.
    
    """
    key = authorize()
    body = {}
    address = "https://api.challonge.com/v1.tournaments/" + tournament + ".xml"
    
    body = {"tournament[sequential_pairings]": "true"}
    r = requests.post(address, data=body, auth=key)
    
    address = "https://api.challonge.com/v1/tournaments/" + tournament +"/participants.xml"
    body = {}
    
    for e in b.iter_ranked():
        body["participant[name]"] = e.name
        r = requests.post(address, data=body, auth=key)
    
    print r.text
    
def save_xml(tournament):
    key = authorize()

    r = requests.get("https://api.challonge.com/v1/tournaments/" + tournament + "/participants.xml", auth=key)

    fname = tournament + "-participants.xml"
    output = open(fname, "w")
    output.write(r.text)
    output.close()

    r = requests.get("https://api.challonge.com/v1/tournaments/" + tournament + "/matches.xml", auth=key)

    fname = tournament + "-matches.xml"
    output = open(fname, "w")
    output.write(r.text)
    output.close()
    
    return fname

    
def _find_match(root, matchid):
    for m in root.iter("match"):
        id = m.find("id").text
        
        if id == matchid:
            return m
            
def _find_top_match(root):
    phase = 0
    m_temp = None
    for m in root.iter("match"):
        if int(m.find("round").text) <= phase:
            continue
        
        phase = int(m.find("round").text)
        m_temp = m
    
    for m in root.iter("match"):
        if phase-1 == int(m.find("round").text):
            return m
    
    return None
    
def generate(matchfile, participantfile=""):
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
    matchref = match.find("player1-prereq-match-id")
    
    if matchref.get("nil") != "true":
        member1 = generate_branch(_find_match(root, matchref.text), root, participants)
    else:
        member1 = generate_participant(match.find("player1-id").text, participants)
    
    matchref = match.find("player2-prereq-match-id")
    if matchref.get("nil") != "true":
        member2 = generate_branch(_find_match(root, matchref.text), root, participants)
    else:
        member2 = generate_participant(match.find("player2-id").text, participants)
        
    return bracket.branchedElement(member1, member2)