from abc import ABC, abstractmethod
from pathlib import Path
import json


class BaseArtScraper(ABC):
    def __init__(self, output_dir=None, skip_existing=True, min_wait=None):
        self.skip_existing = skip_existing
        self.output_dir = output_dir
        self._meta_store = {"link": "",
                            "data": {}}
        self.link = "None"
        self.min_wait = min_wait

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        pass

    def load_link(self, link):
        self.link = link

    @abstractmethod
    def _get_metadata(self):
        pass

    @property
    def meta_fp(self):
        return Path(self.paint_dir, "metadata.json")

    def convert_img_fp(self, img_fp=None, suffix=".png"):
        if img_fp is None:
            if self.output_dir is None:
                raise ValueError("Trying to save file with no path or output dir.")
            img_fp = Path(self.paint_dir, "painting.png")
        elif Path(img_fp).suffix != suffix:
            print(f"Warning: changing file extensions: "
                  f"{Path(img_fp).suffix} -> {suffix}")
            img_fp = Path(Path(img_fp).parent, Path(img_fp).stem+suffix)
        else:
            img_fp = Path(img_fp)
        return img_fp

    def get_metadata(self, link=None, **kwargs):
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
        if meta_fp is None:
            meta_fp = self.meta_fp
        if meta_fp.is_file():
            return
        metadata = self.get_metadata()
        self.paint_dir.mkdir(exist_ok=True)
        with open(meta_fp, "w") as f:
            json.dump(metadata, f)

    @abstractmethod
    def save_image(self, img_fp=None, link=None):
        pass

    def close(self):
        pass
