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
    # Attempt to avoid overlapping element obscuring right arrow button
    #driver.maximize_window()
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

    while True:
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
        # Continue looping if list still has less than total number of artworks
        if(len(elements)) >= num_items:
            break
       # else:
          #  break

    # List to store links to the artist's works
    list_links = []
    # Go through each xpath containing a link to an artwork
    for element in elements:
        # Append to list
        list_links.append(element.get_attribute('href'))

    return list_links
