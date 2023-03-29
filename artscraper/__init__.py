"""Scrape art image and metadata from WikiArt and Google Arts."""

from artscraper.googleart import GoogleArtScraper, random_wait_time
from artscraper.wikiart import WikiArtScraper
from artscraper.artist_links import get_artist_links

__all__ = ["GoogleArtScraper", "WikiArtScraper", "get_artist_links", "random_wait_time"]
