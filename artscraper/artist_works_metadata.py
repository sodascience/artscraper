'''
get_artist_works: Get links to the artist's works, from Google Arts & Culture webpage
get_artist_description: Get description of the artist, from Wikipedia
get_artist_metadata: Get metadata of the artist, from Wikidata
'''

import time
import requests
from selenium import webdriver
import wikipediaapi
from artscraper.googleart import random_wait_time

# SPARQL query to fetch metadata from wikidata

SPARQL_QUERY = '''
SELECT ?familyName ?familyNameLabel ?givenName ?givenNameLabel ?dateOfBirth ?dateOfBirthLabel ?placeOfBirth ?placeOfBirthLabel ?coordinatesBirth ?coordinatesBirthLabel ?latitudeBirth ?latitudeBirthLabel ?longitudeBirth ?longitudeBirthLabel ?dateOfDeath ?dateOfDeathLabel ?placeOfDeath ?placeOfDeathLabel ?coordinatesDeath ?coordinatesDeathLabel ?latitudeDeath ?latitudeDeathLabel ?longitudeDeath ?longitudeDeathLabel ?genre ?genreLabel ?movement ?movementLabel 
WHERE {
  OPTIONAL { wd:person_id wdt:P734 ?familyName. }
  OPTIONAL { wd:person_id wdt:P735 ?givenName. }
  OPTIONAL { wd:person_id wdt:P569 ?dateOfBirth. }
  OPTIONAL { wd:person_id wdt:P19 ?placeOfBirth. }
  OPTIONAL {
    ?placeOfBirth wdt:P625 ?coordinatesBirth.
    BIND(geof:latitude(?coordinatesBirth) AS ?latitudeBirth)
    BIND(geof:longitude(?coordinatesBirth) AS ?longitudeBirth)
  }
  OPTIONAL { wd:person_id wdt:P570 ?dateOfDeath. }
  OPTIONAL { wd:person_id wdt:P20 ?placeOfDeath. }
  OPTIONAL {
    ?placeOfDeath wdt:P625 ?coordinatesDeath.
    BIND(geof:latitude(?coordinatesDeath) AS ?latitudeDeath)
    BIND(geof:longitude(?coordinatesDeath) AS ?longitudeDeath)
  }
  OPTIONAL { wd:person_id wdt:P136 ?genre. }
  OPTIONAL { wd:person_id wdt:P135 ?movement. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
'''

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

    '''
    Parameters
    ----------
    artist_link : Web address of the artist's Google Arts & Culture page

    Returns
    -------
    metadata: Dictionary containing metadata about the artist
    '''

    # Get Wikidata ID of artist
    artist_id = get_artist_wikidata_id(artist_link)

    # Wikidata database to query
    url = 'https://query.wikidata.org/sparql'

    # Replace person_id in SPARQL query with the wikidata ID of the artist
    query = SPARQL_QUERY.replace('person_id', artist_id)

    # Send query request
    request = requests.get(url, params= {'format': 'json', 'query': ''.join(query)}, timeout=10)

    # Convert response to dictionary
    data = request.json()

    # Assemble metadata in a dictionary
    metadata = {
        'family name': get_single_valued_property(data, 'familyName'),
        'given name': get_single_valued_property(data, 'givenName'),
        'date of birth': get_single_valued_property(data, 'dateOfBirth').rsplit('T')[0],
        'place of birth': get_single_valued_property(data, 'placeOfBirth'),
        'latitude of place of birth' :
            float(get_single_valued_property(data, 'latitudeBirth')),
        'longitude of place of birth' :
            float(get_single_valued_property(data, 'longitudeBirth')),
        'date of death': get_single_valued_property(data, 'dateOfDeath').rsplit('T')[0],
        'place of death': get_single_valued_property(data, 'placeOfDeath'),
        'latitude of place of death' :
            float(get_single_valued_property(data, 'latitudeDeath')),
        'longitude of place of death' :
            float(get_single_valued_property(data, 'longitudeDeath')),
        'genres': get_multi_valued_property(data, 'genre'),
        'movements': get_multi_valued_property(data, 'movement')
    }

    return metadata

def get_artist_wikidata_id(artist_link):

    '''
    Parameters
    ----------
    artist_link : Web address of the artist's Google Arts & Culture page

    Returns
    -------
    wikidata_id: Wikidata ID of the artist
    '''

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

def get_single_valued_property(data, query_property):

    '''
    Parameters
    ----------
    data : Data, in JSON format, fetched from Wikidata query
    query_property : Property to be extracted from data

    Returns
    -------
    output_property : Value of extracted property
    '''

    if query_property+'Label' in data['results']['bindings'][0].keys():
        output_property = data['results']['bindings'][0][query_property+'Label']['value']
    else:
        output_property = ''

    return output_property

def get_multi_valued_property(data, query_property):

    '''
    Parameters
    ----------
    data : Data, in JSON format, fetched from Wikidata query
    query_property : Property to be extracted from data

    Returns
    -------
    output_property_list : List of values of extracted property
    '''

    output_property_list = []
    if query_property+'Label' in data['results']['bindings'][0].keys():
        for element in data['results']['bindings']:
            output_property = element[query_property+'Label']['value']
            # Avoid duplicates
            if output_property not in output_property_list:
                output_property_list.append(output_property)

    return output_property_list
