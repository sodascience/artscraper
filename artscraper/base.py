"""Base class for the ArtScraper package.

Any newly defined scrapers should derive themselves from
BaseArtScraper.
"""

import json
from abc import ABC
from abc import abstractmethod
from pathlib import Path


class BaseArtScraper(ABC):
    """Base class for ArtScrapers.

    Currently two ArtScrapers are implemented (WikiScraper and GoogleScraper)
    which derive from this class.

    Parameters
    ----------
    output_dir: Path or str, optional
        Output directory for any scraped images.
    skip_existing: bool, default=True
        If true, skip downloading any existing images.
    min_wait: float
        To avoid going over rate limits, this can be set a floating point
        number, which sets the minimum time between requests.
    """

    def __init__(self, output_dir=None, skip_existing=True, min_wait=None):
        self.skip_existing = skip_existing
        self.output_dir = output_dir

        # Cache of metadata, in case it is needed more than once/later.
        self._meta_store = {"link": "", "data": {}}
        self.link = "None"
        self.min_wait = min_wait

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        pass

    def load_link(self, link):
        """Load an url / webpage.

        Parameters
        ----------
        link: str
            URL to open for subsequent actions.
        """
        self.link = link

    @property
    @abstractmethod
    def paint_dir(self):
        """pathlib.Path: Directory to store the current image/painting."""

    @abstractmethod
    def _get_metadata(self):
        raise NotImplementedError

    @property
    def meta_fp(self):
        """pathlib.Path: Path to metadata file for current artwork."""
        return Path(self.paint_dir, "metadata.json")

    def _convert_img_fp(self, img_fp=None, suffix=".png"):
        """Function to create a path from available information.

        Also changes the suffix of the file if needed.
        """
        if img_fp is None:
            if self.output_dir is None:
                raise ValueError("Trying to save file with no path or output "
                                 "dir.")
            img_fp = Path(self.paint_dir, "artwork.png")
        elif Path(img_fp).suffix != suffix:
            print(f"Warning: changing file extensions: "
                  f"{Path(img_fp).suffix} -> {suffix}")
            img_fp = Path(Path(img_fp).parent, Path(img_fp).stem + suffix)
        else:
            img_fp = Path(img_fp)
        return img_fp

    def get_metadata(self, link=None, **kwargs):
        """Obtain metadata from an url.

        Implementations of the base class should implement
        the _get_metadata method that is called from this method.
        The data is automatically cached, in case it needed later on.

        Arguments
        ---------
        link: str
            The url to the artwork. If not None, it will overwrite the
            currently loaded link. It is the same as calling load_link first,
            and then get_metadata with no link.
        kwargs: dict
            The keyword arguments allow the user to add items to the results.
            This way, if more is known about the artwork from outside sources,
            it can be easily added.

        Returns
        -------
        dict: metadata
            The metadata related to the artwork in the link.
        """
        if link is not None and link != self.link:
            self.load_link(link)

        if self.link == "None":
            raise ValueError("Load link or supply link to get meta data.")

        if self.link == self._meta_store["link"]:
            metadata = self._meta_store["data"]
        else:
            metadata = self._get_metadata()
            metadata["link"] = self.link
            self._meta_store = {
                "link": self.link,
                "data": metadata,
            }
        metadata.update(kwargs)
        return metadata

    def save_metadata(self, meta_fp=None):
        """Save the metadata to a JSON file.

        Arguments
        ---------
        meta_fp: str, Path
            If None, then the default file path is computed with the
            attribute output_dir. If not None, this file is used to dump the
            data.
        """
        if meta_fp is None:
            meta_fp = self.meta_fp
        if meta_fp.is_file():
            return
        metadata = self.get_metadata()
        self.paint_dir.mkdir(exist_ok=True)
        with open(meta_fp, "w", encoding="utf-8") as f:  # pylint: disable=invalid-name
            json.dump(metadata, f)

    @abstractmethod
    def save_image(self, img_fp=None, link=None):
        """Abstract method to save the image to a file.

        Arguments
        ---------
        img_fp: str, Path
            File to save the image to. If the image has a different
            suffix/extension from the supplied image_fp, then it is changed
            and a warning should be printed. If img_fp is None, the default
            destination will be used.
        link: str
            Optionally the url to the artwork can be supplied, which will be
            loaded instead.
        """
        raise NotImplementedError()

    def close(self):
        """Remove any resources that are being used.

        This is non-reversible.
        """
