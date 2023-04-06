'''
get_artist_works: Get artist links from Google Arts & Culture webpage
get_artist_description: Get description of the artist, from Wikipedia
'''

import time
import requests
from selenium import webdriver
import wikipediaapi
from artscraper.googleart import random_wait_time


def get_artist_works(artist_link, min_wait_time):

    '''
    Parameters
    ----------
    artist_link : Web address of the artist's Google Arts & Culture page
    min_wait_time: Minimum time (in seconds) to wait before scrolling to the right

    Returns
    -------
    list_links: List with web addresses of the artist's works on Google Arts & Culture

    '''

    # Launch Firefox browser
    driver = webdriver.Firefox()

    # Get Google Arts & Culture webpage for the artist
    driver.get(artist_link)

    # Locate the section on the page containing the artworks, by searching for the text heading
    element = driver.find_element('xpath', '//*[contains(text(), "Discover this artist")]')

    # Find the parent element corresponding to the text heading
    parent_element = element.find_element('xpath', '../..')

    # Find element which contains number of artworks in the text
    element_with_num_items = parent_element.find_element('xpath', '//h3[contains(text(), "items")]')
    # Extract text containing total number of artworks for this artist
    num_items_text = element_with_num_items.text
    # Total number of artworks for this artist
    num_items = int(num_items_text.split(' ')[0])

    #Initialize list of elements with links to artworks
    elements = []
    while len(elements) < num_items:
        # Find right arrow button
        right_arrow_element = parent_element.find_element('xpath', \
            './/*[contains(@data-gaaction,"rightArrow")]')
        # Click on right arrow button
        driver.execute_script("arguments[0].click();", right_arrow_element)
        # Wait for page to load
        time.sleep(random_wait_time(min_wait=min_wait_time))
        # List of all elements with links to artworks, at this stage
        elements = right_arrow_element.find_elements('xpath', \
            '//*[contains(@href,"/asset/")]')

    # Get the links from the XPath elements
    list_links = [element.get_attribute('href') for element in elements]

    return list_links

def get_artist_description(artist_link):

    '''
    Parameters
    ----------
    artist_link : Web address of the artist's Google Arts & Culture page

    Returns
    -------
    description : String containing description of artist (lead section of Wikipedia article)

    '''

    # Launch Firefox browser
    driver = webdriver.Firefox()

    # Get Google Arts & Culture webpage for the artist
    driver.get(artist_link)

    # Locate the element containing the link to the artist's Wikipedia article
    element = driver.find_element('xpath','//*[contains(@href,"wikipedia")]')
    # Extract the link to the Wikipedia article
    wikipedia_link = element.get_attribute('href')
    # Find the title of the Wikipedia article
    title = wikipedia_link.rsplit('/')[-1]

    # Choose the English Wikipedia
    wiki = wikipediaapi.Wikipedia('en')
    # Get the Wikipedia page
    page = wiki.page(title)
    # Get summary of the page (lead section of the Wikipedia article)
    description = page.summary

    return description

def get_artist_metadata(artist_link):
    
    # Get Wikidata ID of artist
    artist_id = get_artist_wikidata_id(artist_link)
    
    # Wikidata database to query
    url = 'https://query.wikidata.org/sparql'
    
    # SPARQL query
    query = (
        'SELECT ?familyName ?familyNameLabel ',
        '?givenName ?givenNameLabel ',
        '?dateOfBirth ?dateOfBirthLabel ',
        '?placeOfBirth ?placeOfBirthLabel ',
        '?coordinatesBirth ?coordinatesBirthLabel ',
        '?latitudeBirth ?latitudeBirthLabel ',
        '?longitudeBirth ?longitudeBirthLabel ',    
        '?dateOfDeath ?dateOfDeathLabel ',
        '?placeOfDeath ?placeOfDeathLabel ',
        '?coordinatesDeath ?coordinatesDeathLabel ',
        '?latitudeDeath ?latitudeDeathLabel ',
        '?longitudeDeath ?longitudeDeathLabel ',
        '?genre ?genreLabel ',
        '?movement ?movementLabel ',
         '   WHERE ',
         '       {',
                 # Family name
         '       OPTIONAL{ wd:'+artist_id+' wdt:P734 ?familyName .}',    
                 # Given name
         '       OPTIONAL{ wd:'+artist_id+' wdt:P735 ?givenName .}', 
                 # Date of birth
         '       OPTIONAL{ wd:'+artist_id+' wdt:P569 ?dateOfBirth .}', 
                 # Place of birth
         '       OPTIONAL{ wd:'+artist_id+' wdt:P19 ?placeOfBirth .}',   
                 # Coordinates of place of birth
         '       OPTIONAL{ ?placeOfBirth wdt:P625 ?coordinatesBirth .', 
                 # Latitude of place of birth
         '       BIND(geof:latitude(?coordinatesBirth) AS ?latitudeBirth) .', 
                 # Longitude of place of birth
         '       BIND(geof:longitude(?coordinatesBirth) AS ?longitudeBirth) .}',  
                 # Date of death
         '       OPTIONAL{ wd:'+artist_id+' wdt:P570 ?dateOfDeath .}', 
                 # Place of death
         '       OPTIONAL{ wd:'+artist_id+' wdt:P20 ?placeOfDeath .}',   
                 # Coordinates of place of death
         '       OPTIONAL{ ?placeOfDeath wdt:P625 ?coordinatesDeath .',
                 # Latitude of place of death            
         '       BIND(geof:latitude(?coordinatesDeath) AS ?latitudeDeath) .', 
                 # Longitude of place of death
         '       BIND(geof:longitude(?coordinatesDeath) AS ?longitudeDeath) .}', 
                 # Genre(s)
         '       OPTIONAL{ wd:'+artist_id+' wdt:P136 ?genre .}', 
                 # Movement(s)
         '       OPTIONAL{ wd:'+artist_id+' wdt:P135 ?movement .}',    
         '       SERVICE wikibase:label { bd:serviceParam wikibase:language "en" .}'
         '       }'
    )
        
    # Send query request
    r = requests.get(url, params= {'format': 'json', 'query': "".join(query)})
    
    # Convert to dictionary
    data = r.json()
    
    # Name information
    try:
        family_name = data['results']['bindings'][0]['familyNameLabel']['value']
    except:
        family_name = ''
        
    try:
        given_name = data['results']['bindings'][0]['givenNameLabel']['value']
    except:
        given_name = '' 
        
    # Birth information
    try:
        date_of_birth = data['results']['bindings'][0]['dateOfBirthLabel']['value'].rsplit('T')[0]
    except:
        date_of_birth = ''
        
    try:
        place_of_birth = data['results']['bindings'][0]['placeOfBirthLabel']['value']
    except:
        place_of_birth = ''
        
    try:
        place_of_birth_latitude = data['results']['bindings'][0]['latitudeBirth']['value']
        place_of_birth_longitude = data['results']['bindings'][0]['longitudeBirth']['value']
    except:
        place_of_birth_latitude = ''
        place_of_birth_longitude = ''
        
    # Death information
    try:
        date_of_death = data['results']['bindings'][0]['dateOfDeathLabel']['value'].rsplit('T')[0]
    except:
        date_of_death = ''
        
    try:
        place_of_death = data['results']['bindings'][0]['placeOfDeathLabel']['value']
    except:
        place_of_death = ''
        
    try:
        place_of_death_latitude = data['results']['bindings'][0]['latitudeDeath']['value']
        place_of_death_longitude = data['results']['bindings'][0]['longitudeDeath']['value']
    except:
        place_of_death_latitude = ''
        place_of_death_longitude = ''
        
    # Genre(s)
    genres = []
    try:
        for element in data['results']['bindings']:
            genre = element['genreLabel']['value']
            # Avoid duplicates
            if genre not in genres:
                genres.append(genre)
    except:
        pass
    
    # Movements(s)
    try:
        movements = []
        for element in data['results']['bindings']:
            movement = element['movementLabel']['value']
            # Avoid duplicates
            if movement not in movements:
                movements.append(movement)
    except:
        pass
    
    metadata = {
        'family name': family_name,
        'given name': given_name,
        'date of birth': date_of_birth,
        'place of birth': place_of_birth,
        'latitude of place of birth' : round(float(place_of_birth_latitude),2),
        'longitude of place of birth' : round(float(place_of_birth_longitude),2),
        'date of death': date_of_death,
        'place of death': place_of_death,
        'latitude of place of death' : round(float(place_of_death_latitude),2),
        'longitude of place of death' : round(float(place_of_death_longitude),2),
        'genres': [genre for genre in genres],
        'movements': [movement for movement in movements],
    }
    
    return metadata

def get_artist_wikidata_id(artist_link):
    
    # Launch Firefox browser
    driver = webdriver.Firefox()

    # Get Google Arts & Culture webpage for the artist
    driver.get(artist_link)

    # Locate the element containing the link to the artist's Wikipedia article
    element = driver.find_element('xpath','//*[contains(@href,"wikipedia")]')
    # Extract the link to the Wikipedia article
    wikipedia_link = element.get_attribute('href')
    
    # Get Wikipedia page for the artist
    driver.get(wikipedia_link)
    # Find element containing text about Wikidata
    element = driver.find_element('xpath','//*[contains(text(),"Wikidata item")]')
    # Find parent element of this element
    parent_element = element.find_element('xpath', '..')
    # Extract the link to the Wikidata page
    wikidata_link = parent_element.get_attribute('href')
    # Find the Wikidata ID of the artist
    wikidata_id = wikidata_link.rsplit('/')[-1]
    
    return wikidata_id