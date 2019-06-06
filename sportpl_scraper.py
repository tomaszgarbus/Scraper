import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from lxml.html import document_fromstring
from typing import List, Callable, Set, Optional

from utils import is_link_relative


def sportpl_follow_link(link: str):
    return (link.startswith('http://www.sport.pl/pilka')
            or link.startswith('/pilka'))


def sportpl_remove_scripts(soup: BeautifulSoup):
    for tag in soup.findChildren():
        if tag.name == 'script':
            tag.extract()
        else:
            sportpl_remove_scripts(tag)


def sportpl_get_article_content(soup: BeautifulSoup) -> Optional[str]:
    art_contents = soup.find_all(id='gazeta_article_body')
    for tag in art_contents:
        sportpl_remove_scripts(tag)
    if art_contents:
        article_text = document_fromstring(
            '\n'.join(list(map(str, art_contents)))).text_content()
        print('::', soup.title.text, '::')
        print(article_text)
        return article_text


class SportPlArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as
    possible.
    """
    def __init__(self,
                 home: str,
                 domain: str,
                 limit: int = -1,
                 follow_link: Callable[[str], bool] = sportpl_follow_link):
        """
        A constructor for a scraper object.
        :param home: The starting page.
        :param home: The domain of the scraped portal.
        :param limit: Maximum number of visited web pages. If set to -1, then
                      there is no limit.
        :param follow_link: A function determining whether to follow a link or
                            not.
        """
        super(SportPlArticlesScraper, self).__init__()

        self.home = home
        self.domain = domain
        self.limit = limit
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

    def _visit_page(self, page_url: str) -> None:
        """
        Processes a single page during the DFS scraping procedure.

        :param page_url: URL to the page.
        """
        print("Visiting %s; queued elements %d; %d on queue; #articles %d" %
              (page_url, len(self.visited_or_queued), len(self.queue),
               self.articles_found))

        # Parses the webpage and fetches the list of links.
        try:
            with urllib.request.urlopen(page_url) as response:
                html = response.read()
        except urllib.error.HTTPError:
            print("404")
            return

        soup = BeautifulSoup(html, 'html.parser')
        article_text = sportpl_get_article_content(soup)
        if article_text:
            self.articles_found += 1
        # Selects the links to follow.
        links_to_follow: List[str] = list(map(lambda a: a['href'],
                                              soup.find_all('a')))
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

    def run(self):
        while self.queue:
            # Pops the first webpage from the queue.
            page = self.queue[0]
            self.queue = self.queue[1:]

            self._visit_page(page_url=page)