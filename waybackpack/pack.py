from .settings import DEFAULT_ROOT
from .session import Session
from .asset import Asset
from .cdx import search
import hashlib
import sys, os
import logging
logger = logging.getLogger(__name__)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class Pack(object):
    def __init__(self,
        snapshots,
        uniques_only=False,
        session=None):

        self.session = session or Session()
        self.assets = [ Asset(snapshot["original"], snapshot["timestamp"]) for snapshot in snapshots ]

    def download_to(self, directory,
        raw=False,
        root=DEFAULT_ROOT,
        ignore_errors=False):

        for asset in self.assets:
            url = asset.original_url
            prefix = "http://" if urlparse(url).scheme == "" else  ""
            full_url = prefix + url
            parsed_url = urlparse(full_url)
            path_head, path_tail = os.path.split(parsed_url.path)
            if path_tail == "":
                path_tail = "index.html"

            filedir = os.path.join(
                directory,
                asset.timestamp,
                parsed_url.netloc,
                path_head.lstrip("/")
            )

            filepath = os.path.join(filedir, path_tail)

            logger.info(
                "Fetching {0} @ {1}".format(
                    asset.original_url, 
                    asset.timestamp)
            )

            try:
                content = asset.fetch(
                    session=self.session,
                    raw=raw,
                    root=root
                )
            except Exception as e:
                if ignore_errors == True:
                    ex_name = ".".join([ e.__module__, e.__class__.__name__ ])
                    logger.warn("ERROR -- {0} @ {1} -- {2}: {3}".format(
                        asset.original_url,
                        asset.timestamp,
                        ex_name,
                        e
                    ))
                    continue
                else:
                    raise

            try:
                os.makedirs(filedir)
            except OSError:
                pass
            with open(filepath, "wb") as f:
                logger.info("Writing to {0}\n".format(filepath))
                f.write(content)
