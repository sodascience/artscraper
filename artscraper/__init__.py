"""Scrape art image and metadata from WikiArt and Google Arts."""

from artscraper.googleart import GoogleArtScraper, random_wait_time
from artscraper.wikiart import WikiArtScraper
from artscraper.artist_links import get_artist_links
from artscraper.artist_works_metadata import get_artist_works
from artscraper.artist_works_metadata import get_artist_description, get_artist_metadata

__all__ = ["GoogleArtScraper", "WikiArtScraper",
           "get_artist_links", "get_artist_works",
           "get_artist_description", "get_artist_metadata",
           "random_wait_time"]
