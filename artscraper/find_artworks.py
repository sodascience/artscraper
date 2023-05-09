'''
Class containing, among others, the following methods:

get_artist_works: Get links to the artist's works, from Google Arts & Culture webpage
get_artist_description: Get description of the artist, from Wikipedia
get_artist_metadata: Get metadata of the artist, from Wikidata

'''
from pathlib import Path

import time
import re
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import wikipediaapi

from artscraper.functions import random_wait_time

class FindArtworks:
    '''
    Class for finding artworks and metadata for an artist,
    given the link to their Google Arts & Culture webpage
    '''

    def __init__(self, artist_link, executable_path='geckodriver',
                 output_dir='./data', sparql_query= None, min_wait_time=5):

        # Link to artist's Google Arts & Culture webpage
        self.artist_link = artist_link
        # Path to geckodriver
        self.executable_path = executable_path
        # Directory to which the data is to be written
        # Create it if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        # Directory to which the data is to be written
        self.output_dir = output_dir
        # Minimum wait time between two clicks while scrolling a webpage
        self.min_wait_time = min_wait_time

        # SPARQL query to fetch metadata from wikidata
        if sparql_query is None:
            # Default SPARQL query
            self.sparql_query = '''
                SELECT
                ?familyName ?familyNameLabel
                ?givenName ?givenNameLabel
                ?sexOrGender ?sexOrGenderLabel
                ?dateOfBirth ?dateOfBirthLabel
                ?placeOfBirth ?placeOfBirthLabel
                ?latitudeOfPlaceOfBirth ?latitudeOfPlaceOfBirthLabel
                ?longitudeOfPlaceOfBirth ?longitudeOfPlaceOfBirthLabel
                ?dateOfDeath ?dateOfDeathLabel
                ?placeOfDeath ?placeOfDeathLabel
                ?latitudeOfPlaceOfDeath ?latitudeOfPlaceOfDeathLabel
                ?longitudeOfPlaceOfDeath ?longitudeOfPlaceOfDeathLabel
                ?countryOfCitizenship ?countryOfCitizenshipLabel
                ?residence ?residenceLabel
                ?workLocation ?workLocationLabel
                ?genre ?genreLabel
                ?movement ?movementLabel
                WHERE {
                  OPTIONAL { wd:person_id wdt:P734 ?familyName. }
                  OPTIONAL { wd:person_id wdt:P735 ?givenName. }
                  OPTIONAL { wd:person_id wdt:P21 ?sexOrGender. }
                  OPTIONAL { 
                      wd:person_id wdt:P569 ?dateTimeOfBirth.
                      BIND (xsd:date(?dateTimeOfBirth) AS ?dateOfBirth)
                  }
                  OPTIONAL { wd:person_id wdt:P19 ?placeOfBirth. }
                  OPTIONAL {
                    ?placeOfBirth wdt:P625 ?coordinatesBirth.
                    BIND(geof:latitude(?coordinatesBirth) AS ?latitudeOfPlaceOfBirth)
                    BIND(geof:longitude(?coordinatesBirth) AS ?longitudeOfPlaceOfBirth)
                  }
                  OPTIONAL { 
                      wd:person_id wdt:P569 ?dateTimeOfDeath.
                      BIND (xsd:date(?dateTimeOfDeath) AS ?dateOfDeath)
                  }              
                  OPTIONAL { wd:person_id wdt:P20 ?placeOfDeath. }
                  OPTIONAL {
                    ?placeOfDeath wdt:P625 ?coordinatesDeath.
                    BIND(geof:latitude(?coordinatesDeath) AS ?latitudeOfPlaceOfDeath)
                    BIND(geof:longitude(?coordinatesDeath) AS ?longitudeOfPlaceOfDeath)
                  }
                  OPTIONAL { wd:person_id wdt:P27 ?countryOfCitizenship. }
                  OPTIONAL { wd:person_id wdt:P551 ?residence. }
                  OPTIONAL { wd:person_id wdt:P937 ?workLocation. }
                  OPTIONAL { wd:person_id wdt:P136 ?genre. }
                  OPTIONAL { wd:person_id wdt:P135 ?movement. }
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                '''
        else:
            self.sparql_query = sparql_query
        
        # Open web browser
        self.driver = webdriver.Firefox(executable_path=self.executable_path)


    def __enter__(self):
        return self


    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        # Close web browser
        self.driver.close()

        
    def get_artist_information(self):

        '''
        Returns
        -------
        artist_works, artist_description, artist_metadata : All information about the artist

        '''

        artist_works = self.get_artist_works()
        artist_description = self.get_artist_description()
        artist_metadata = self.get_artist_metadata()

        return artist_works, artist_description, artist_metadata


    def save_artist_information(self):

        '''
        Save information (artist_works, artist_description, artist_metadata) about the artist

        '''

        artist_works, artist_description, artist_metadata = self.get_artist_information()
        artist_name = self.get_wikipedia_article_title()

        # Create directory for artist
        pathname_directory = self.output_dir + '/' + artist_name
        Path(pathname_directory).mkdir(parents=True, exist_ok=True)

        # Filenames for artist's works, description, metadata
        artist_works_file = pathname_directory + '/' + 'works.txt'
        artist_description_file = pathname_directory + '/' + 'description.txt'
        artist_metadata_file = pathname_directory + '/' + 'metadata.txt'

        # Save artist's works, description, metadata 
        with open(artist_works_file, 'w', encoding='utf-8') as file:
            for link in artist_works:
                file.write(f'{link}\n')
        with open(artist_description_file, 'w', encoding='utf-8') as file:
            file.write(artist_description)
        with open(artist_metadata_file, 'w', encoding='utf-8') as file:
            for key,value in artist_metadata.items():
                file.write(f'{key} : {value}\n')
                

    def get_artist_works(self):

        '''
        Returns
        -------
        list_links: List with web addresses of the artist's works on Google Arts & Culture

        '''

        # Get Google Arts & Culture webpage for the artist
        self.driver.get(self.artist_link)

        # Locate the section on the page containing the artworks, by searching for the text heading
        element = self.driver.find_element('xpath', '//*[contains(text(), "Discover this artist")]')

        # Find the parent element corresponding to the text heading
        parent_element = element.find_element('xpath', '../..')

        # Find right arrow button
        right_arrow_element = parent_element.find_element('xpath', \
            './/*[contains(@data-gaaction,"rightArrow")]')
        
        # Check if right arrow button can still be clicked
        while right_arrow_element.get_attribute('tabindex') is not None:
            # Find right arrow button
            right_arrow_element = parent_element.find_element('xpath', \
                './/*[contains(@data-gaaction,"rightArrow")]')
            # Click on right arrow button
            self.driver.execute_script("arguments[0].click();", right_arrow_element)
            # Wait for page to load
            time.sleep(random_wait_time(min_wait=self.min_wait_time))
            
        # List of all elements with links to artworks
        elements = right_arrow_element.find_elements('xpath', \
                '//*[contains(@href,"/asset/")]')
            
        # Get the links from the XPath elements
        list_links = [element.get_attribute('href') for element in elements]

        return list_links
    

    def get_artist_description(self):

        '''
        Returns
        -------
        description : String containing description of artist (lead section of Wikipedia article)

        '''

        # Get title of artist's Wikipedia article
        title = self.get_wikipedia_article_title()
        # Choose the English Wikipedia
        wiki = wikipediaapi.Wikipedia('en')
        # Get the Wikipedia page
        page = wiki.page(title)
        # Get summary of the page (lead section of the Wikipedia article)
        description = page.summary

        return description

    def get_artist_metadata(self):

        '''
        Returns
        -------
        metadata: Dictionary containing metadata about the artist

        '''

        # Get Wikidata ID of artist
        artist_id = self.get_artist_wikidata_id()

        # Wikidata database to query
        url = 'https://query.wikidata.org/sparql'

        # Replace person_id in SPARQL query with the wikidata ID of the artist
        query = self.sparql_query.replace('person_id', artist_id)

        # Send query request
        request = requests.get(url, params= {'format': 'json', 'query': ''.join(query)}, timeout=10)

        # Convert response to dictionary
        data = request.json()

        # Extract properties searched by the SPARQL query
        properties_query = re.findall(r"\?[^\s]*Label\b", self.sparql_query)

        # Remove redundant prefix and suffix
        properties = [property.removeprefix('?').removesuffix('Label') for property in properties_query]

        # Assemble metadata in a dictionary
        metadata = {re.sub('(\B[A-Z])', r' \1', property).lower(): self._get_property(data, property) for property in properties}
        
        return metadata
    

    def get_wikipedia_article_link(self):

        '''
        Returns
        -------
        wikipedia_link : Web address of the artist's Wikipedia article'

        '''

        # Get Google Arts & Culture webpage for the artist
        self.driver.get(self.artist_link)

        # Locate the element containing the link to the artist's Wikipedia article
        element = self.driver.find_element('xpath','//*[contains(@href,"wikipedia")]')
        # Extract the link to the Wikipedia article
        wikipedia_link = element.get_attribute('href')

        return wikipedia_link

    def get_wikipedia_article_title(self):

        '''
        Returns
        -------
        title : String containing the title of the artist's Wikipedia article

        '''

        # Get the link to the artist's Wikipedia article
        wikipedia_link = self.get_wikipedia_article_link()

        # Get title of artist's Wikipedia article
        title = wikipedia_link.rsplit('/')[-1]

        return title

    def get_artist_wikidata_id(self):

        '''
        Returns
        -------
        wikidata_id: Wikidata ID of the artist
        '''

        # Get Google Arts & Culture webpage for the artist
        self.driver.get(self.artist_link)

        # Locate the element containing the link to the artist's Wikipedia article
        element = self.driver.find_element('xpath','//*[contains(@href,"wikipedia")]')
        # Extract the link to the Wikipedia article
        wikipedia_link = element.get_attribute('href')

        # Get Wikipedia page for the artist
        self.driver.get(wikipedia_link)
        # Find element containing text about Wikidata
        element = self.driver.find_element('xpath','//*[contains(text(),"Wikidata item")]')
        # Find parent element of this element
        parent_element = element.find_element('xpath', '..')
        # Extract the link to the Wikidata page
        wikidata_link = parent_element.get_attribute('href')
        # Find the Wikidata ID of the artist
        wikidata_id = wikidata_link.rsplit('/')[-1]

        return wikidata_id


    def _get_property(self, data, query_property):

        '''
        Parameters
        ----------
        data : Data, in JSON format, fetched from Wikidata query
        query_property : Property to be extracted from data
        Returns
        -------
        output_property : Value of extracted property
        '''
        '''
        Parameters
        ----------
        data : Data, in JSON format, fetched from Wikidata query
        query_property : Property to be extracted from data
        Returns
        -------
        output_property_list : Value(s) of extracted property
        '''

        output_property_list = []
        if query_property+'Label' in data['results']['bindings'][0].keys():
            for element in data['results']['bindings']:
                output_property = element[query_property+'Label']['value']
                # Avoid duplicates
                if output_property not in output_property_list:
                    output_property_list.append(output_property)
            if len(output_property_list)==1:
                output_property_list = output_property_list[0]
            return output_property_list

        # Property doesn't exist
        return ''
