'''
Get artist links from Google Arts & Culture webpage
'''

import time
from selenium import webdriver
from artscraper.googleart import random_wait_time


def get_artist_works(artist_link, min_wait_time):

    '''
    Parameters
    ----------
    artist_link : Web address of the artist's Google Arts & Culture page
    min_wait_time: Minimum time (in seconds) to wait before scrolling to the right

    Returns
    -------
    list_works: List with web addresses of the artist's works on Google Arts & Culture

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
