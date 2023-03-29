from selenium import webdriver
from artscraper import random_wait_time
import time


def get_artist_links(webpage):
    
    # Launch Firefox browser
    driver = webdriver.Firefox()
    
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
    
    # List to store artist links
    list_links = []
    # Go through each xpath containing an artist link
    for element in elements:
        # Append to list
        list_links.append(element.get_attribute('href'))

    return list_links
