"""File for packaging ArtScraper."""

# based on https://github.com/pypa/sampleproject - MIT License

from setuptools import find_packages
from setuptools import setup

setup(
    name='artscraper',
    version='0.1.0',
    author='ODISSEI Social Data Science Team',
    description='Package for scraping artworks from WikiArt and GoogleArt',
    long_description='Package for scraping artworks from WikiArt and GoogleArt',
    packages=find_packages(exclude=['data', 'docs', 'tests', 'examples']),
    python_requires='~=3.6',
    install_requires=[
        "requests",
        "selenium",
        "beautifulsoup4"
    ]
)
