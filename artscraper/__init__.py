"""Scrape art image and metadata from WikiArt and Google Arts."""

from artscraper.googleart import GoogleArtScraper
from artscraper.wikiart import WikiArtScraper

__all__ = ["GoogleArtScraper", "WikiArtScraper"]
