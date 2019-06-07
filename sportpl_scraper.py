"""
Scraper for sport.pl. The goal is to make it more universal, but for now I'm
avoiding premature optimizations/refactorings.
"""
import http.client
import random
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from lxml.html import document_fromstring
from typing import List, Callable, Set, Optional

from article import Article
from utils import is_link_relative


def sportpl_follow_link(link: str):
    return (link.startswith('http://www.sport.pl/pilka')
            or link.startswith('/pilka')) and 'pilka/2' not in link


def sportpl_remove_scripts(soup: BeautifulSoup):
    for tag in soup.findChildren():
        if tag.name == 'script':
            tag.extract()
        else:
            sportpl_remove_scripts(tag)


def sportpl_make_article(soup: BeautifulSoup, source_url: str) -> \
        Optional[Article]:
    """
    Builds an Article object.
    :param soup: A BeautifulSoup object - a parsed article.
    :param source_url: Source URL.
    :return: An Article object or None.
    """
    art_contents = soup.find_all(id='gazeta_article_body')
    for tag in art_contents:
        sportpl_remove_scripts(tag)
    if art_contents:
        article_text = document_fromstring(
            '\n'.join(list(map(str, art_contents)))).text_content()
        article_date = (soup.find(class_='article_date') or
                        soup.find(id='gazeta_article_date')).time['datetime']
        return Article(title=soup.title.text,
                       datetime=article_date,
                       text=article_text,
                       source_url=source_url)
    return None


class SportPlArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as
    possible.
    """
    def __init__(self,
                 home: str,
                 domain: str,
                 follow_link: Callable[[str], bool] = sportpl_follow_link):
        """
        A constructor for a scraper object.
        :param home: The starting page.
        :param home: The domain of the scraped portal.
        :param follow_link: A function determining whether to follow a link or
                            not.
        """
        super(SportPlArticlesScraper, self).__init__()

        self.home = home
        self.domain = domain
        self.follow_link = follow_link

        # Creates a queue of web pages URLs to visit.
        self.queue: List[str] = [self.home]
        # Creates a set of visited or queued links.
        self.visited_or_queued: Set[str] = set()

        self.articles_found = 0

    def _preprocess_link(self, link: str) -> str:
        if link.startswith('\\\'') and link.endswith('\\\''):
            link = link[2:-2]
        if is_link_relative(link):
            link = self.domain + link
        return link

    def _visit_page(self, page_url: str) -> Optional[Article]:
        """
        Processes a single page during the DFS scraping procedure.

        :param page_url: URL to the page.
        :return: An article, if there was one on the page, or None.
        """
        print("Visiting %s; queued elements %d; %d on queue; #articles %d" %
              (page_url, len(self.visited_or_queued), len(self.queue),
               self.articles_found))

        # Parses the webpage and fetches the list of links.
        try:
            with urllib.request.urlopen(page_url) as response:
                html = response.read()
        except (urllib.error.HTTPError, urllib.error.URLError,
                http.client.IncompleteRead, UnicodeEncodeError):
            print("http read failed")
            return

        soup = BeautifulSoup(html, 'html.parser')
        article = sportpl_make_article(soup, page_url)
        if article:
            self.articles_found += 1

        # Selects the links to follow.
        links_with_href = list(filter(lambda a: a.has_attr('href'),
                                      soup.find_all('a')))
        links_to_follow: List[str] = list(map(lambda a: a['href'],
                                              links_with_href))
        links_to_follow = list(filter(self.follow_link, links_to_follow))
        links_to_follow = list(map(self._preprocess_link, links_to_follow))

        for link in links_to_follow:
            if link in self.visited_or_queued:
                # Link has already been visited, there is a cycle in the link
                # graph.
                continue
            # Appends the link url to the end of the queue.
            self.queue.append(link)
            self.visited_or_queued.add(link)

        if article:
            return article

    def run(self):
        while self.queue:
            # Pops random webpage from the queue.
            # Why random? To avoid falling into an endless process of visiting
            # all single-matche-pages.
            idx = random.randint(0, len(self.queue)-1)
            page = self.queue[idx]
            self.queue = self.queue[:idx] + self.queue[idx+1:]

            article = self._visit_page(page_url=page)
            if article:
                yield article