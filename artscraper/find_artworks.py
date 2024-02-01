'''
Class containing, among others, the following methods:

get_artist_works: Get links to the artist's works, from Google Arts & Culture webpage
get_artist_description: Get description of the artist, from Wikipedia
get_artist_metadata: Get metadata of the artist, from Wikidata

'''

from pathlib import Path

import time
import re
from urllib.parse import urlparse
from urllib.parse import unquote
import json
import requests

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

import wikipediaapi

from artscraper.functions import random_wait_time

class FindArtworks:
    '''
    Class for finding artworks and metadata for an artist,
    given the link to their Google Arts & Culture webpage
    unquote   '''

    # Allow __init__ function to have more than 5 arguments
    # pylint: disable-msg=too-many-arguments

    def __init__(self, artist_link,
                 output_dir='./data', sparql_query= None, min_wait_time=5):

        # Link to artist's Google Arts & Culture webpage
        self.artist_link = artist_link
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
                ?pseudonym ?pseudonymLabel
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
                ?occupation ?occupationLabel
                WHERE {
                  OPTIONAL { wd:person_id wdt:P734 ?familyName. }
                  OPTIONAL { wd:person_id wdt:P735 ?givenName. }
                  OPTIONAL { wd:person_id wdt:P742 ?pseudonym. }
                  OPTIONAL { wd:person_id wdt:P21 ?sexOrGender. }
                  OPTIONAL {
                      wd:person_id wdt:P569 ?dateTimeOfBirth.
                      BIND (xsd:date(?dateTimeOfBirth) AS ?dateOfBirth)
                  }
                  OPTIONAL {
                      wd:person_id wdt:P19 ?placeOfBirth.
                      ?placeOfBirth wdt:P625 ?coordinatesBirth.
                      BIND(geof:latitude(?coordinatesBirth) AS ?latitudeOfPlaceOfBirth)
                      BIND(geof:longitude(?coordinatesBirth) AS ?longitudeOfPlaceOfBirth)
                  }
                  OPTIONAL {
                      wd:person_id wdt:P570 ?dateTimeOfDeath.
                      BIND (xsd:date(?dateTimeOfDeath) AS ?dateOfDeath)
                  }
                  OPTIONAL {
                      wd:person_id wdt:P20 ?placeOfDeath.
                      ?placeOfDeath wdt:P625 ?coordinatesDeath.
                      BIND(geof:latitude(?coordinatesDeath) AS ?latitudeOfPlaceOfDeath)
                      BIND(geof:longitude(?coordinatesDeath) AS ?longitudeOfPlaceOfDeath)
                  }
                  OPTIONAL { wd:person_id wdt:P27 ?countryOfCitizenship. }
                  OPTIONAL { wd:person_id wdt:P551 ?residence. }
                  OPTIONAL { wd:person_id wdt:P937 ?workLocation. }
                  OPTIONAL { wd:person_id wdt:P136 ?genre. }
                  OPTIONAL { wd:person_id wdt:P135 ?movement. }
                  OPTIONAL { wd:person_id wdt:P106 ?occupation. }
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                '''
        else:
            self.sparql_query = sparql_query

        # Open web browser
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))


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
        artist_name = self.get_artist_name()
        # Create directory for artist
        pathname_directory = self.output_dir + '/' + artist_name
        Path(pathname_directory).mkdir(parents=True, exist_ok=True)
        # Filenames for artist's works, description, metadata
        artist_works_file = pathname_directory + '/' + 'works.txt'
        artist_description_file = pathname_directory + '/' + 'description.txt'
        artist_metadata_file = pathname_directory + '/' + 'metadata.json'
        # Save artist's works, description, metadata
        with open(artist_works_file, 'w', encoding='utf-8') as file:
            for link in artist_works:
                file.write(f'{link}\n')
        with open(artist_description_file, 'w', encoding='utf-8') as file:
            if artist_description is not None:
                file.write(artist_description)
        with open(artist_metadata_file, 'w', encoding='utf-8') as file:
            if artist_metadata is not None:
                json.dump(artist_metadata, file, ensure_ascii=False)


    def get_artist_name(self):

        '''
        Return artist's name, with parts thereof being separated by underscores
        '''

        # Artist link
        artist_link = self.artist_link

        # Split the link by forward slashes
        parts = artist_link.split('/')
        # Extract the artist's name (separated by dashes)
        artist_name_string = parts[4]
        artist_name_string = unquote(artist_name_string)

        # Split the artist's name into component parts
        artist_name_parts = artist_name_string.split('-')
        # Capitalize each component
        artist_name_capitalized_parts = []
        for part in artist_name_parts:
            part = part.capitalize()
            artist_name_capitalized_parts.append(part)

        # Artist's name, separated by underscores
        artist_name = ('_').join(artist_name_capitalized_parts)

        return artist_name

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

        # Initialize total number of artworks
        # (set to number of artworks by artist with the most artworks)
        total_num_artworks = 200000

        # Find number of artists
        # Find elements with tag name 'h3'
        items_elements = parent_element.find_elements('tag name', 'h3')
        for element in items_elements:
            if 'items' in element.text:
                match = re.search(r'\d+', element.text)
                if match:
                    total_num_artworks = int(match.group())
                    break

        # Find right arrow element
        def _find_right_arrow_element(parent_element):

            right_arrow_element = parent_element.find_element('xpath', \
                './/*[contains(@data-gaaction,"rightArrow")]')

            return right_arrow_element

        # Get list of artwork links
        def _get_list_links(parent_element):

            # Find right arrow button
            right_arrow_element = parent_element.find_element('xpath', \
                './/*[contains(@data-gaaction,"rightArrow")]')

            # List of all elements with links to artworks
            elements = right_arrow_element.find_elements('xpath', \
                '//*[contains(@href,"/asset/")]')

            # Get the links from the XPath elements
            list_links = [element.get_attribute('href') for element in elements]

            return list_links

        # Click on right arrow
        def _click_on_right_arrow(parent_element):

            # Find right arrow button
            right_arrow_element = parent_element.find_element('xpath', \
                './/*[contains(@data-gaaction,"rightArrow")]')
            # Click on right arrow button
            self.driver.execute_script("arguments[0].click();", right_arrow_element)

        list_links = _get_list_links(parent_element)

        # Initialize count of number of iterations for which the number of artworks remains the same
        n_tries = 0

        while (len(list_links) < total_num_artworks and
               not (total_num_artworks == 0 and n_tries > 3)):

            # Save current number of artworks
            old_num_artworks = len(list_links)

            # Find right arrow element
            right_arrow_element =  _find_right_arrow_element(parent_element)

            # Check if right arrow button can still be clicked
            if right_arrow_element.get_attribute('tabindex') is not None:

                # Click on right arrow
                _click_on_right_arrow(parent_element)

                # Wait for page to load
                time.sleep(random_wait_time(min_wait=self.min_wait_time))

                # Obtain new list of artworks
                list_links = _get_list_links(parent_element)

            if len(list_links) == old_num_artworks:
                # Count number of iterations for which the number of artworks remains the same
                n_tries = n_tries + 1
            else:
                n_tries = 0

        return list_links


    def get_artist_description(self):

        '''
        Returns
        -------
        description : String containing description of artist (lead section of Wikipedia article)

        '''

        # Get title of artist's Wikipedia article
        title = self.get_wikipedia_article_title()

        # Return None if no Wikipedia article exists
        if title is None:
            return None

        # Get link to Wikipedia article
        wikipedia_article_link = self.get_wikipedia_article_link()
        # Parse the URL
        parsed_url = urlparse(wikipedia_article_link)
        # Find the language of the Wikipedia article
        language_code = parsed_url.netloc.split('.')[0]

        # Choose the Wikipedia corresponding to the language code
        wiki = wikipediaapi.Wikipedia(language_code)
        # Get the Wikipedia page
        page = wiki.page(title)
        # Get summary of the page (lead section of the Wikipedia article)
        description = page.summary

        description = unquote(description)

        return description

    def get_artist_metadata(self):

        '''
        Returns
        -------
        metadata: Dictionary containing metadata about the artist

        '''

        # Get Wikidata ID of artist
        artist_id = self.get_artist_wikidata_id()
        if artist_id is None:
            return None

        # Wikidata database to query
        url = 'https://query.wikidata.org/sparql'

        # Replace person_id in SPARQL query with the wikidata ID of the artist
        query = self.sparql_query.replace('person_id', artist_id)

        # Send query request
        request = requests.get(url, params={'format': 'json', \
                            'query': ''.join(query)}, timeout=120)

        # Convert response to dictionary
        data = request.json()

        # Extract properties searched by the SPARQL query
        properties_query = re.findall(r"\?[^\s]*Label\b", self.sparql_query)

        # Remove redundant prefix and suffix
        properties = [property.removeprefix('?').removesuffix('Label') \
                      for property in properties_query]

        # Assemble metadata in a dictionary
        metadata = {re.sub(r'(\B[A-Z])', r' \1', property).lower(): \
                    self._get_property(data, property) for property in properties}

        return metadata


    def get_wikipedia_article_link(self):

        '''
        Returns
        -------
        wikipedia_link : Web address of the artist's Wikipedia article'

        '''

        # Get Google Arts & Culture webpage for the artist
        self.driver.get(self.artist_link)
        # Allow bare-except
        # pylint: disable=W0702
        try:
            # Locate the element containing the link to the artist's Wikipedia article
            element = self.driver.find_element('xpath','//*[contains(@href,"wikipedia")]')
        except:
            return None

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

        if wikipedia_link is not None:
            # Get title of artist's Wikipedia article
            title = wikipedia_link.rsplit('/')[-1]
            title = unquote(title)
            return title

        return None

    def get_artist_wikidata_id(self):

        '''
        Returns
        -------
        wikidata_id: Wikidata ID of the artist
        '''

        # Get the link to the Wikipedia article
        wikipedia_link = self.get_wikipedia_article_link()

        # Get Wikipedia page for the artist
        if wikipedia_link is not None:
            self.driver.get(wikipedia_link)
        else:
            return None

        # Find element containing the link to the Wikidata page
        element = self.driver.find_element('xpath','//*[contains(@href,"www.wikidata.org")]')
        # Extract the link to the Wikidata page
        wikidata_link = element.get_attribute('href')
        # Specify pattern of Wikidata ID
        pattern = r'Q\d+'
        # Search for pattern in the Wikidata link
        match = re.search(pattern, wikidata_link)
        # Find the Wikidata ID of the artist
        wikidata_id = match.group(0)

        return wikidata_id


    def _get_property(self, data, query_property):

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
                output_property = unquote(output_property)
                # Avoid duplicates
                if output_property not in output_property_list:
                    output_property_list.append(output_property)
            if len(output_property_list)==1:
                output_property_list = output_property_list[0]
            return output_property_list

        # Property doesn't exist
        return ''
