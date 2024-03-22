
# ArtScraper

ArtScraper is a tool to download images and metadata for artworks available on
WikiArt (www.wikiart.org/) and Google Arts & Culture
(artsandculture.google.com/).

Functionality:
- `WikiArt` and `Google Arts & Culture`: Download images and metadata from a list of artworks' urls
- `Google Arts & Culture`: Download all images and metadata in the site, or from specific artists

## 1. Installation and setup

The ArtScraper package can be installed with pip, which automatically installs
the python dependencies:

```
pip install artscraper
```


## 2. Downloading art from WikiArt

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

An example of fetching data is shown below and in the [notebook](examples/example_artscraper.ipynb). 

```python

from artscraper import WikiArtScraper

art_url = "https://www.wikiart.org/en/edvard-munch/anxiety-1894"

with WikiArtScraper(output_dir="data") as scraper:
    scraper.load_link(art_url)
    scraper.save_metadata() 
    scraper.save_image()

```

This will store both the image itself and the metadata in separate folders. If
you use ArtScraper in this way, it will skip images/metadata that is already
present. Remove the directory to force it to redownload it. 

Results:

[<img src="https://uploads5.wikiart.org/images/edvard-munch/anxiety-1894.jpg" weight="20">](https://www.wikiart.org/en/edvard-munch/anxiety-1894)


## 3. Downloading art from Google Arts & Culture

To download data from GoogleArt it is necessary to install 
[Firefox](https://www.mozilla.org/en-US/firefox/new/) and `geckodriver`. Geckodriver is installed automatically when you run the code for the first time.

ArtScraper will open a new Firefox window, navigate to the image, zoom on it and take a screenshot of it. It will take a few seconds. Do not minimize that browser, and do not let the screensaver go on.


### 3.1 Downloading art from Google Arts & Culture using artworks' urls

An example of fetching data is shown below and in the [notebook](examples/example_artscraper.ipynb). 

```python
from artscraper import GoogleArtScraper

art_url = "https://artsandculture.google.com/asset/anxiety-edvard-munch/JgE_nwHHS7wTPw"

with GoogleArtScraper() as scraper:
    scraper.load_link(art_url)
    metadata = scraper.get_metadata() #or scraper.save_metadata()
    scraper.save_image("data/anxiety_munch.jpg")
    print(metadata) 

```


### 3.2 Downloading all art from Google Arts & Culture 

See [example notebook](examples/example_collect_all_artworks.ipynb).

The final structure of the results will be
- data
  - artist_links.txt (All artists, with one url per line) 
  - Artist_1
    - description.txt (Description of artist, from wikidata)
    - metadata.json (Metadata of arist, from wikidata)
    - works.txt (All artworks, with one url per line)
    - works 
      - work1
        - artwork.png (Artwork image)
        - metadata.json (Metadata of artwork, from Google Art and Culture)
      - work2
        - ...
  - Artist_2
    - ... 


A full example (but please check the [example notebook](examples/example_collect_all_artworks.ipynb) to add retries):

```python
from artscraper.find_artists import get_artist_links
# Get links for all artists, as a list
output_dir = "data"
artist_urls = get_artist_links(min_wait_time=1, output_file=f'{output_dir}/artist_links.txt')

# Find_artworks for each artist
for artist_url in artist_urls:
    with FindArtworks(artist_link=artist_url, output_dir=output_dir, 
                      min_wait_time=min_wait_time) as scraper:
            # Save list of artworks, the description, and metadata for an artist
            scraper.save_artist_information()
            # Find artist directory
            artist_dir = output_dir + '/' + scraper.get_artist_name() 

    # Scrape artworks
    with GoogleArtScraper(artist_dir + '/' + 'works', min_wait=min_wait_time) as subscraper:
        # Get list of links to this artist's works 
        with open(artist_dir+'/'+'works.txt', 'r') as file:
            artwork_links = [line.rstrip() for line in file]  
        # Download all artwork link (slow)
        for url in artwork_links:
            print(f'artwork URL: {url}')
            subscraper.save_artwork_information()
```


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
