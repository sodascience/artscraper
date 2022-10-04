"""Module for the WikiArt scraper class."""

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from artscraper.base import BaseArtScraper


class WikiArtScraper(BaseArtScraper):
    """Class to interact with the WikiArt API."""

    def __init__(self, output_dir=None, skip_existing=True, min_wait=0.3, timeout=150):
        super().__init__(output_dir, skip_existing, min_wait=min_wait)
        self.timeout = timeout
        self._get_API_keys()

        # Try to use the previous session, can be deleted if expired.
        try:
            with open(".wiki_session", "r", encoding="utf-8") as f:
                self.session_key = f.read()
        except FileNotFoundError:
            self._new_session()
            with open(".wiki_session", "w", encoding="utf-8") as f:
                f.write(self.session_key)
        self.last_request = None

    @property
    def paint_dir(self):
        metadata = self.get_metadata()
        return Path(self.output_dir, metadata["id"])

    def _get_API_keys(self):
        """Read the API secret/access key from the current directory

        If the file .wiki_api does not exist, ask for the access and secret
        keys.
        """
        try:
            with open(".wiki_api", "r", encoding="utf-8") as f:
                self.API_access_key, self.API_secret_key, *_ = f.read().split(
                    "\n")
            return
        except FileNotFoundError:
            print("No API keys found in current directory.")
            print("WikiArt API keys can be obtained from "
                  "'https://www.wikiart.org/en/App/GetApi'.")
            self.API_access_key = input("WikiArt Access Key? ")
            self.API_secret_key = input("WikiArt Secret Key? ")

            str_out = "\n".join([self.API_access_key, self.API_secret_key, ""])
            with open(".wiki_api", "w", encoding="utf-8") as f:
                f.write(str_out)

    def _new_session(self):
        """Create a new session and store the session key"""
        login_page = "https://www.wikiart.org/en/Api/2/login"
        response = requests.get(login_page,
                                params={
                                    "accessCode": self.API_access_key,
                                    "secretCode": self.API_secret_key
                                },
                                timeout=self.timeout)
        self.session_key = json.loads(response.text)["SessionKey"]
        self.last_request = time.time()

    def _get_content(self, url, params):
        """Get data through the WikiArt API with rate limits"""
        params["authSessionKey"] = self.session_key
        if self.last_request is not None:
            time_elapsed = time.time() - self.last_request
            if time_elapsed < self.min_wait:
                time.sleep(self.min_wait - time_elapsed)
        response = requests.get(url, params=params, timeout=self.timeout)
        self.last_request = time.time()
        return json.loads(response.text)

    def _find_by_artist_painting(self):
        """Find the painting by searching for artist + painting name"""
        link_dirs = _link_dirs(self.link)
        terms = " ".join(link_dirs).replace("-", " ")
        try:
            int(terms[-4:])
            terms = terms[:-5]
        except ValueError:
            pass

        url = "https://www.wikiart.org/en/api/2/PaintingSearch"
        params = {"term": terms}
        meta_data = self._get_content(url, params)
        painting_list = meta_data["data"]
        for paint_meta in painting_list:
            try:
                return self._check_metadata(paint_meta, link_dirs)
            except ValueError:
                pass

        raise ValueError("Cannot find painting by artist + painting")

    def _find_by_scrape(self):
        """This is a nasty bit of regex to get the painting ID"""
        link_dirs = _link_dirs(self.link)
        response = requests.get(self.link, timeout=self.timeout)
        # We try two different regexes to get the painting ID.
        p_rgx = re.compile(r"paintingId = '(.+?')")
        try:
            paint_id = p_rgx.search(response.text).group(0)[14:-1]
        except AttributeError:
            try:
                p_rgx = re.compile(r'data-painting-id="(.+?)"')
                paint_id = p_rgx.search(response.text).group(0)[18:-1]
            except AttributeError as error:
                raise ValueError("Cannot find painting by scrape.") from error
        return self._check_metadata(paint_id, link_dirs)

    def _check_metadata(self, paint_meta, link_dirs):
        """Get the meta data from a painting with validation"""
        if isinstance(paint_meta, str):
            paint_id = paint_meta
        else:
            paint_id = paint_meta["id"]
        paint_data = self.info_from_painting_id(paint_id)
        if (paint_data["artistUrl"] == link_dirs[0]
                and paint_data["url"] == link_dirs[1]):
            return paint_data
        raise ValueError("Painting is not the right one.")

    def _find_by_artist(self):
        """Get the meta data by searching for all paintings by the artist

        This is generally very slow, since a request for each of the paintings
        has to be made. It also has the problem that it seems like the
        pagination tokens do not work, so this method doesn't always work for
        artists with a lot of artworks, since higher page numbers are
        inaccessible.
        """
        url = "https://www.wikiart.org/en/api/2/PaintingSearch"
        link_dirs = _link_dirs(self.link)
        artist = link_dirs[0].replace("-", " ")
        has_more = True
        meta_data = []
        params = {"term": artist}
        # Get a list of all the paintings by the artist.
        while has_more:
            new_meta = self._get_content(url, {"term": artist})
            if len(new_meta["data"]) == 0:
                break
            meta_data.extend(new_meta["data"])
            params['paginationToken'] = new_meta["paginationToken"]
            has_more = new_meta["hasMore"]

        # Check each painting until we find the right one.
        for paint_meta in meta_data:
            try:
                return self._check_metadata(paint_meta, link_dirs)
            except ValueError:
                pass
        raise ValueError("Cannot find painting by artist.")

    def _get_metadata(self):
        """Find a painting from a link through 3 different methods"""
        try:
            return self._find_by_artist_painting()
        except ValueError:
            pass
        try:
            return self._find_by_scrape()
        except ValueError:
            pass
        return self._find_by_artist()

    def info_from_painting_id(self, painting_id):
        """Get the meta data from a painting_id"""
        url = "https://www.wikiart.org/en/api/2/Painting"
        params = {"id": painting_id}
        return self._get_content(url, params)

    def save_image(self, img_fp=None, link=None):
        metadata = self.get_metadata(link=link)
        img_url = metadata["image"]
        path = urlparse(img_url).path
        suffix = Path(path).suffix
        img_fp = self._convert_img_fp(img_fp, suffix)

        if self.skip_existing and img_fp.is_file():
            return
        img_data = requests.get(img_url, timeout=self.timeout).content

        if self.output_dir:
            self.paint_dir.mkdir(exist_ok=True)
        with open(img_fp, "wb") as f:
            f.write(img_data)


def _link_dirs(link):
    return urlparse(link).path.split("/")[-2:]
