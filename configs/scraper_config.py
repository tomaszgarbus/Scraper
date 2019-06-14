from bs4 import BeautifulSoup
from typing import Optional

from article import Article
import requests


class ScraperConfig:
    def __init__(self):
        pass

    def home(self) -> str:
        """
        Starting page, provided as an absolute URL.
        :return: An absolute URL as string.
        """
        raise NotImplementedError()

    def domain(self) -> str:
        """
        The domain of the visited portal. It will be used to create absolute
        URLs from relative URLs by concatenation.
        :return: The domain as string.
        """
        raise NotImplementedError()

    def state_cache_fname(self) -> str:
        """
        Filename to the ScraperState cache. it will be placed in `cache` folder.
        :return: Filename to the state cache.
        """
        raise NotImplementedError()

    def should_follow_link(self, link: str) -> bool:
        """
        Given a link, determines whether scraper should queue it for visit.
        :param link: An absolute URL.
        :return: A boolean
        """
        raise NotImplementedError()

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        """
        If the visited web page contains an article, extracts its content and
        builds an Article object. Otherwise returns None.
        :param soup: A BeautifulSoup representation of visited page.
        :param source_url: Absolute URL of the visited page.
        :return: Either an Article object or None.
        """
        raise NotImplementedError()

    def fetch_page(self, page_url) -> str:
        """
        Function fetching the web page given its URL. For some websites it might
        be necessary to override it (e.g. to handle polish characters correctly
        or sleep 1 second to not get banned).
        :param page_url: An absolute URL of the page to fetch.
        :return: Raw HTML content of the web page.
        """
        return requests.get(page_url).text
