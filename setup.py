# based on https://github.com/pypa/sampleproject - MIT License

from setuptools import setup, find_packages

setup(
    name='artscraper',
    version='0.1.0',
    author='ArtScraper Development Team',
    description='Package for scraping artworks from WikiArt and GoogleArt',
    long_description='Package for scraping artworks from WikiArt and GoogleArt',
    packages=find_packages(exclude=['data', 'docs', 'tests', 'examples']),
    python_requires='~=3.6',
    install_requires=[
        "requests",
        "selenium",
        "beautifulsoup4",
        "numpy",
    ]
)
