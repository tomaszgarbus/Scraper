"""
A configurable articles scraper.
"""
import http.client
import os
import pickle
import requests
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from typing import List, Set, Optional, Iterable

from article import BaseArticle
from configs.scraper_config import ScraperConfig
from utils import is_link_relative


class ScraperState:
    """
    State of the Scraper. This State should contain all information necessary
    to resume an interrupted scraper.
    """
    def __init__(self):
        # Queue of links to visit. Each link on the queue is an absolute URL
        # string.
        self.queue: List[str] = []
        # Links that either have already been visited or are on the queue.
        self.visited_or_queued: Set[str] = set()
        # Number of found articles.
        self.articles_found = 0


def load_cached_state(fname: str) -> Optional[ScraperState]:
    """
    Tries to load cached ScraperState.
    :param fname: Filename inside 'cache/' directory.
    :return: A ScraperState instance or None.
    """
    state: Optional[ScraperState] = None
    if os.path.exists(os.path.join('cache', fname)):
        with open(os.path.join('cache', fname), 'rb') as file:
            state = pickle.load(file)
    return state


def cache_state(fname: str, state: ScraperState) -> None:
    """
    Caches the ScraperState instance to 'cache/' directory.
    :param fname: Filename inside 'cache/' folder.
    :param state: A ScraperState instance to cache.
    """
    with open(os.path.join('cache', fname), 'wb+') as file:
        pickle.dump(state, file)


class ArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as
    possible.
    """
    def __init__(self,
                 config: ScraperConfig):
        """
        A constructor for a scraper object.
        :param config: An instance of ScraperConfig subclass.
        """
        super(ArticlesScraper, self).__init__()

        self.home = config.home()
        self.domain = config.domain()
        self.follow_link = config.should_follow_link
        self.extract_article = config.extract_article
        self.state_cache_fname = config.state_cache_fname()
        self.get_request = config.fetch_page
        self.config = config

        self.state = (load_cached_state(self.state_cache_fname) or
                      ScraperState())
        self.state.queue.append(self.home)
        self.state.visited_or_queued.add(self.home)

    def _preprocess_link(self, link: str) -> str:
        """
        Preprocesses the link to fix common issues and transform it into an
        absolute URL. Note that this operation may not produce a valid URL
        and in such case it should fail the `self.follow_link` predicate.
        :param link: An URL, absolute or relative.
        :return: An absolute URL.
        """
        if link.startswith('\\\'') and link.endswith('\\\''):
            link = link[2:-2]
        if is_link_relative(link):
            link = self.domain + link
        return link

    def _visit_page(self, page_url: str) -> Optional[BaseArticle]:
        """
        Processes a single page during the DFS scraping procedure.

        :param page_url: URL to the page.
        :return: An article, if there was one on the page, or None.
        """
        print("Visiting %s; queued elements %d; %d on queue; #articles %d" %
              (page_url, len(self.state.visited_or_queued),
               len(self.state.queue), self.state.articles_found))

        # Parses the webpage and fetches the list of links.
        try:
            html = self.get_request(page_url)
        except (urllib.error.HTTPError, urllib.error.URLError,
                http.client.IncompleteRead, UnicodeEncodeError,
                http.client.InvalidURL, requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError, TimeoutException,
                UnicodeError) as err:
            print("http read failed", err)
            return None

        soup = BeautifulSoup(html, 'html.parser')
        article = self.extract_article(soup, page_url)
        if article:
            self.state.articles_found += 1

        # Selects the links to follow.
        links_with_href = list(filter(lambda a: a.has_attr('href'),
                                      soup.find_all('a')))
        links_to_follow: List[str] = list(map(lambda a: a['href'],
                                              links_with_href))
        links_to_follow = list(map(self._preprocess_link, links_to_follow))
        links_to_follow = list(filter(self.follow_link, links_to_follow))

        for link in links_to_follow:
            if link in self.state.visited_or_queued:
                # Link has already been visited, there is a cycle in the link
                # graph.
                continue
            # Appends the link url to the end of the queue.
            self.state.queue.append(link)
            self.state.visited_or_queued.add(link)

        return article

    def run(self) -> Iterable[BaseArticle]:
        """
        Runs the scraper.
        :return: Yields all found articles.
        """
        while self.state.queue:
            page = self.state.queue[0]
            self.state.queue = self.state.queue[1:]

            article = self._visit_page(page_url=page)
            if article:
                yield article

    def checkpoint(self) -> None:
        """
        Caches the state on disk.
        """
        cache_state(self.state_cache_fname, self.state)
