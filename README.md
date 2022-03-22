# ArtScraper

## Install

The ArtScraper package can be installed with pip:

`pip install .`

Then install the selenium driver. This is platform dependent, but the one used for this project is `geckodriver`, which is linked to Firefox. Make sure that you have a recent version of geckodriver, because selenium uses features that were only recently introduced in geckodriver.

## Fetch data

To fetch data, put the file `deviant.xlsx` in the directory `data/raw`, and run `get_wiki_data.py` and `get_google_data.py`. You might need to rerun them a few times. I don't know exactly why, but at some point google seems to return white images. It might be because of screensavers? In any case, I generally run the following command to remove the image directories with white images:

`sh for F in $(find data/output/google_arts/ -iname painting.png -size -55k); do rm -r $(dirname $F); done`

Obviously be careful with bash scripts like these and makes sure you are in the right directory.

Reruns will skip existing data (but the lastly made directory for the google data should be removed). The data will be under `data/output`: metadata for the WikiArts dataset and metadata + pictures for the google data.

## Clean data

Run the python script `clean_google_meta.py` after fetching the data. It removes and renames/merges a lot of columns from the initial meta data, making it more easy to work with, while not being as complete.

## Explore the metadata

The notebook `GoogleArts.ipynb` explores the meta data by using TF-IDF and applying logistic regression on the results. The coefficients are found to indicate which words are positively or negatively predicting the deviance of an art work according to the models.
