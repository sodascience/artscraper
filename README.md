# ArtScraper

ArtScraper is a tool to download images and metadata for artworks available on WikiArt and GoogleArt. 


## Installation and setup

The ArtScraper package can be installed with pip, which automatically installs the python dependencies:

`pip install .`


### WikiArt

To download data from WikiArt, it is necessary to obtain [API](https://www.wikiart.org/en/App/GetApi) keys. After obtaining them, you can put them in a file called `.wiki_api` in the working directory for your script. The format is: the API access key, a new line, the API secret key, and a new line, e.g.:

```
7e57a60844
3defc62d8f
```

Alternatively, when ArtScraper doesn't detect the file `.wiki_api`, it will ask for the API keys.

### GoogleArt

For the GoogleArt scraper it is necessary to install a non-python dependency, which is the selenium driver. This is platform dependent, but the one used for this project is `geckodriver`, which is linked to Firefox. Make sure that you have a recent version of geckodriver, because selenium uses features that were only recently introduced in geckodriver. Naturally, Firefox itself also needs to be installed. We have only tested the scraping on Linux/Firefox and OS X/Firefox.

On Linux, geckodriver is most likely available through the package manager for your distribution. On OS X, it is the easiest to install it through either [brew](https://formulae.brew.sh/formula/geckodriver#default) or [macports](https://ports.macports.org/port/geckodriver/). Depending on your settings, you might need to add the directory where the geckodriver resides to the PATH variable.


## Download images and metadata (interactive)

An example of fetching data is shown in an [examples](examples/interactive.ipynb) notebook. Assuming the WikiArtScraper is used, we can download the data from a link with:

```python

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

We can see that every time we want to download either images or metadata, we first load the URL into the scraper. For the GoogleArt implementation, releasing the resources with `scraper.close` will ensure that the browser is closed. The scraper should not be used after that.

## Download images and metadata (automatic)

For many use cases it might be useful to download a series of links and store them in a consistent way.

```python

with GoogleArtScraper("data/output/googlearts") as scraper:
	for url in some_links:
		scraper.load_link(url)
		scraper.save_metadata()
		scraper.save_image()
```

This will store both the image itself and the metadata in separate folders. If you use ArtScraper in this way, it will skip images/metadata that is already present. Remove the directory to force it to redownload it.

## Known issues

Sometimes the `GoogleArtScraper` returns white images (tested on OS X), which is most likely due to the screensaver kicking in. Apart from disabling the screensaver, the following shell command might be useful to remove most of the white images (if the data is in `data/output/google_arts`: 

`sh for F in $(find data/output/google_arts/ -iname painting.png -size -55k); do rm -r $(dirname $F); done`

Be careful with bash scripts like these and makes sure you are in the right directory.
