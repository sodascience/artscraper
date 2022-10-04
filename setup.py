"""File for packaging ArtScraper."""

# based on https://github.com/pypa/sampleproject - MIT License

from setuptools import find_packages
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='artscraper',
    version='0.1.1',
    author='ODISSEI Social Data Science Team',
    description='Package for scraping artworks from WikiArt and GoogleArt',
    long_description=readme(),
    long_description_content_type='text/markdown',
    keywords='artscraper wikiart artsandculture',
    license='MIT',
    url='https://github.com/sodascience/artscraper',
    packages=find_packages(exclude=['data', 'docs', 'tests', 'examples']),
    python_requires='~=3.6',
    install_requires=[
        "requests",
        "selenium",
        "beautifulsoup4"
    ]
)
