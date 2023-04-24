'''
Get artist links from Google Arts & Culture webpage
'''

import time
from selenium import webdriver
from artscraper.functions import random_wait_time

def get_artist_links(webpage='https://artsandculture.google.com/category/artist', executable_path=None, output_file=None):
    '''
    Parameters
    ----------
    webpage : Web address of Google Arts & Culture artists page
    executable_path: Path to geckodriver
    output_file: File to which the list of links is to be written

    Returns
    -------
    list_links : List with Google Arts & Culture web addresses for all artists
    '''

    # Launch Firefox browser
    driver = webdriver.Firefox(executable_path=executable_path)

    # Get Google Arts & Culture webpage listing all artists
    driver.get(webpage)

    # Get scroll height after first time page load
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(random_wait_time(min_wait=1))
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Find xpaths containing artist links
    elements = driver.find_elements('xpath', '//*[contains(@href,"categoryId=artist")]')

    # Close driver
    driver.close()
    
    # List to store artist links
    list_links = []
    # Go through each xpath containing an artist link
    for element in elements:
        # Append to list
        list_links.append(element.get_attribute('href'))
        
    if output_file:        
        with open('output_file', 'w') as file:
            for element in list_links:
                file.write(element)
                file.write('\n')
            
    return list_links
