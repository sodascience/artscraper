from pathlib import Path
from random import random
from time import sleep
from urllib.parse import urlparse
import time
import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from artscraper.base import BaseArtScraper


class GoogleArtScraper(BaseArtScraper):
    def __init__(self, output_dir=None, skip_existing=True, min_wait=5):
        super().__init__(output_dir, skip_existing, min_wait=min_wait)
        self.wd = webdriver.Firefox()
        self.last_request = time.time()-100

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.wd.close()

    def load_link(self, link):
        if link == self.link:
            return False
        self.link = link

        if self.output_dir is not None:
            if (self.paint_dir.is_dir() and self.skip_existing
                    and Path(self.paint_dir, "metadata.json").is_file()
                    and Path(self.paint_dir, "painting.png").is_file()):
                return False
            self.paint_dir.mkdir(exist_ok=True, parents=True)

        self.wait(self.min_wait)
        self.wd.get(link)
        return True

    @property
    def paint_dir(self):
        paint_id = "_".join(urlparse(self.link).path.split("/")[-2:])
        return Path(self.output_dir, paint_id)

    def wait(self, min_wait, max_wait=None, update=True):
        time_elapsed = time.time() - self.last_request
        wait_time = random_wait_time(min_wait, max_wait) - time_elapsed
        if wait_time > 0:
            sleep(wait_time)
        if update:
            self.last_request = time.time()

    def get_main_text(self):
        self.wait(self.min_wait, update=False)
        try:
            elem = self.wd.find_element(
                "xpath",
                "/html/body/div[3]/div[3]/div/div/div[5]/section[1]/div")
        except NoSuchElementException:
            return ''
        if elem.get_attribute("id").startswith("metadata-"):
            return ''
        innerHTML = elem.get_attribute("innerHTML")
        return BeautifulSoup(innerHTML, features="html.parser").text

    def _get_metadata(self):
        if self.output_dir is not None and self.meta_fp.is_file():
            with open(self.meta_fp, "r") as f:
                metadata = json.load(f)
            return metadata

        paint_id = urlparse(self.link).path.split("/")[-1]
        self.wait(self.min_wait, update=False)
        elem = self.wd.find_element("xpath", f'//*[@id="metadata-{paint_id}"]')
        inner_HTML = elem.get_attribute("innerHTML")
        soup = BeautifulSoup(inner_HTML, features="html.parser")

        paragraph_HTML = soup.find_all("li")
        metadata = {}
        metadata["main_text"] = self.get_main_text()
        for par in paragraph_HTML:
            name = par.find("span", text=True).contents[0].lower()[:-1]
            metadata[name] = par.text[len(name)+2:]
        metadata["id"] = paint_id
        return metadata

    def get_image(self):
        self.wait(self.min_wait)
        elem = self.wd.find_element(
            "xpath", "/html/body/div[3]/div[3]/div/div/div[2]/div[3]")
        webdriver.ActionChains(self.wd).move_to_element(elem).click(
            elem).perform()
        self.wait(self.min_wait*2, update=False)
        elem = self.wd.find_element(
            "xpath", "/html/body/div[3]/div[3]/div/div/div[2]/div[3]")
        img = elem.screenshot_as_png
        self.wait(self.min_wait)
        self.wd.find_element("xpath", "/html/body").send_keys(Keys.ESCAPE)
        return img

    def save_image(self, img_fp=None, link=None):
        if link is not None:
            self.load_link(link)

        img_fp = self._convert_img_fp(img_fp, suffix=".png")

        if self.skip_existing and img_fp.is_file():
            return
        with open(img_fp, "wb") as f:
            f.write(self.get_image())

    def close(self):
        self.wd.close()


def random_wait_time(min_wait=5, max_wait=None):
    if max_wait is None:
        max_wait = 3*min_wait
    alpha = 1.5
    beta = alpha - 1
    b = min_wait
    c = max_wait
    a = -beta/(c**-beta - b**-beta)

    def cdf(x):
        return a/beta * (b**-beta - x**-beta)

    def inv_cdf(x):
        return (b**-beta - beta*x/a)**(-1/beta)

    return inv_cdf(random())
