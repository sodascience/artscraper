
# ArtScraper

ArtScraper is a tool to download images and metadata for artworks available on
WikiArt (www.wikiart.org/) and Google Arts & Culture
(artsandculture.google.com/).


## Installation and setup

The ArtScraper package can be installed with pip, which automatically installs
the python dependencies:

```
pip install https://github.com/sodascience/artscraper.git
```


### WikiArt

To download data from WikiArt it is necessary to obtain
[API](https://www.wikiart.org/en/App/GetApi) keys. After obtaining them, you
can put them in a file called `.wiki_api` in the working directory for your
script. The format is: the API access key, a new line, the API secret key, and
a new line, e.g.:

```
7e57a60844
3defc62d8f
```

Alternatively, when ArtScraper doesn't detect the file `.wiki_api`, it will
ask for the API keys.

### Google Arts & Culture

To download data from GoogleArt it is necessary to install 
[Firefox](https://www.mozilla.org/en-US/firefox/new/) and `geckodriver`. 

There are two options to download the geckodriver.
- Using a package manager (recommended on Linux/OS X): On Linux, geckodriver 
is most likely available through the package manager for your distribution
(e.g. on Ubuntu `sudo apt install firefox-geckodriver`. On OS X, it is the 
easiest to install it through either [brew](https://formulae.brew.sh/formula/geckodriver#default) or [macports](https://ports.macports.org/port/geckodriver/) (e.g. `brew install geckodriver`). Depending on your settings, you might need to add the directory where the geckodriver resides to the PATH variable. 
- Downloading it [from here](https://github.com/mozilla/geckodriver/releases) and making it available to the code. For example in Windows you can download the file `geckodriver-v0.31.0-win64.zip`, place the driver in the directory of your code, and specify the path when you initialize the GoogleArtScraper. For example:
```python
with GoogleArtScraper(geckodriver_path="./geckodriver.exe") as scraper:
    ...
```

Make sure that you have a recent version of geckodriver, because selenium (a non-python dependency used in the GoogleArt scraper) uses features that were only recently introduced 
in geckodriver. We have only tested the scraping on Linux/Firefox and OSX/Firefox.


## Download images and metadata (interactive)

An example of fetching data is shown in an
[example](examples/example_artscraper.ipynb) notebook. 

Assuming the WikiArtScraper
is used, we can download the data from a link with:

```python

from artscraper import WikiArtScraper

scraper = WikiArtScraper()

# Load the URL into the scraper.
scraper.load_link("some URL")

# Get the metadata
metadata = scraper.get_metadata()

# Save the image to some local file
scraper.save_image("wiki.jpg")

# Release resources
scraper.close()
```

We can see that every time we want to download either images or metadata, we
first load the URL into the scraper. For the GoogleArt implementation,
releasing the resources with `scraper.close` will ensure that the browser is
closed. The scraper should not be used after that.

## Download images and metadata (automatic)

An example of fetching data is shown in an
[example](examples/example_artscraper.ipynb) notebook.

For many use cases it might be useful to download a series of links and store
them in a consistent way.

```python

from artscraper import GoogleArtScraper

with GoogleArtScraper("data/output/googlearts") as scraper:
    for url in some_links:
        scraper.load_link(url)
        scraper.save_metadata()
        scraper.save_image()
```

This will store both the image itself and the metadata in separate folders. If
you use ArtScraper in this way, it will skip images/metadata that is already
present. Remove the directory to force it to redownload it.

## Get list of all artists from Google Arts & Culture website

See [example notebook](examples/example_collect_all_artworks.ipynb). A list with the Google Arts& Culture web addresses of all artists is returned.
```python
from artscraper import get_artist_links

# Get links for all artists, as a list. The links are also saved in a file.
artist_urls = get_artist_links(executable_path='geckodriver', min_wait_time=1, output_file='artist_links.txt')
```

## Get links to an artist's works
A list of all works by a particular artist, specified by the address of their Google Arts & Culture webpage, is returned.
  
```python
# Find links to artworks for a particular artist, from their Google Arts & Culture webpage url
    with FindArtworks(artist_link=artist_url, output_dir=output_dir, min_wait_time=1) as scraper:
		    # Get list of artist's works
            artwork_links = scraper.get_artist_works()
```

## Get metadata about an artist
Metadata for the artist is returned.
```python
# Get metadata for a particular artist, from their Google Arts & Culture webpage url
    with FindArtworks(artist_link=artist_url, output_dir=output_dir, min_wait_time=1) as scraper:
		    # Get list of artist's works
            artwork_links = scraper.get_artist_metadata()
```

## Collect data about all artists, and all their artworks
From a list containing links to all the artists, the following are saved, for each artist:
1. List containing all works by the artist
2. Description of the artist
3. Metadata of the artist
4. Image and metadata of each artwork by the artist
```python
for artist_url in artist_urls:
    with FindArtworks(artist_link=artist_url, output_dir=output_dir, min_wait_time=1) as scraper:
            # Save list of works, description, and metadata for an artist
            scraper.save_artist_information()
            # Get list of links to this artist's works 
            artwork_links = scraper.get_artist_works()
            # Create directory for this artist
            artist_dir = output_dir + '/' + scraper.get_wikipedia_article_title()
    # Scrape artworks
    with GoogleArtScraper(artist_dir + '/' + 'works', min_wait=1) as subscraper:
        # Go through each artwork link
        for url in artwork_links:
            subscraper.load_link(url)
            subscraper.save_metadata()
            subscraper.save_image()
```

## Troubleshooting

Sometimes the `GoogleArtScraper` returns white images (tested on OS X), which
is most likely due to the screensaver kicking in. Apart from disabling the
screensaver, the following shell command might be useful to remove most of the
white images (if the data is in `data/output/google_arts`:

```
sh for F in $(find data/output/google_arts/ -iname painting.png -size -55k); do rm -r $(dirname $F); done
```

Be careful with bash scripts like these and makes sure you are in the right
directory.

## Contributing

Contributions are what make the open source community an amazing place
to learn, inspire, and create. Any contributions you make are **greatly
appreciated**.

Please refer to the
[CONTRIBUTING](https://github.com/sodascience/artscraper/blob/main/CONTRIBUTING.md)
file for more information on issues and pull requests.

## License and citation

The package `artscraper` is published under an MIT license. When using `artscraper` for academic work, please cite:

    Schram, Raoul, Garcia-Bernardo, Javier, van Kesteren, Erik-Jan, de Bruin, Jonathan, & Stamkou, Eftychia. (2022). 
    ArtScraper: A Python library to scrape online artworks (0.1.1). Zenodo. https://doi.org/10.5281/zenodo.7129975


## Contact

This project is developed and maintained by the [ODISSEI Social Data
Science (SoDa)](https://odissei-data.nl/nl/soda/) team.

<img src="soda_logo.png" alt="SoDa logo" width="250px"/>

Do you have questions, suggestions, or remarks? File an issue in the issue
tracker or feel free to contact the team via
https://odissei-data.nl/en/using-soda/.
