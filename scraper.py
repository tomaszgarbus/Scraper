import urllib.request, urllib.error
from html.parser import HTMLParser
from typing import List, Dict, Callable, Set
from utils import is_link_relative


class ArticleParser(HTMLParser):
    def __init__(self):
        super(ArticleParser, self).__init__()
        self.links = []
        # Number of open 'article' tags while traversing the DOM tree.
        self.article_tags_depth = 0
        self.article_text = ''

    def error(self, message):
        print("ERROR", message)
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            # Converts the list of attributes to a dictionary.
            attrs_dict = {}
            for (k, v) in attrs:
                attrs_dict[k] = v
            # Appends the link to the list.
            self.links.append(attrs_dict)
        if tag == 'article':
            # Increases the count of nested 'article' tags.
            self.article_tags_depth += 1

    def handle_endtag(self, tag):
        if tag == 'article':
            # Decreases the count of nested 'article' tags.
            self.article_tags_depth -= 1

    def handle_data(self, data):
        super().handle_data(data)
        if self.article_tags_depth > 0:
            self.article_text += data

    def get_links(self) -> List[Dict[str, str]]:
        """
        Returns a list of links found in the article.
        :return: A list of dictionaries, where keys and values corresponds to the 'a' tag attributes.
        """
        return self.links

    def get_article_text(self) -> str:
        return self.article_text


class ArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as possible.
    """
    def __init__(self,
                 home: str,
                 domain: str,
                 limit: int = -1,
                 follow_link: Callable[[Dict], bool] = (lambda _: True)):
        """
        A constructor for a scraper object.
        :param home: The starting page.
        :param home: The domain of the scraped portal.
        :param limit: Maximum number of visited web pages. If set to -1, then there is no limit.
        :param follow_link: A function determining whether to follow a link or not.
        """
        super(ArticlesScraper, self).__init__()

        self.home = home
        self.domain = domain
        self.limit = limit
        self.follow_link = follow_link

        # Creates a queue of web pages URLs to visit.
        self.queue: List[str] = [self.home]
        # Creates a set of visited or queued links.
        self.visited_or_queued: Set[str] = set()

    def _preprocess_link(self, link: Dict) -> None:
        """
        Performs a number of heuristics to make the link followable.

        :param link: A link presented as a dictionary of (attribute, attribute value) pairs.
        """
        if 'href' in link:
            if link['href'].startswith('\\\'') and link['href'].endswith('\\\'') and len(link['href']) >= 4:
                link['href'] = link['href'][2:-2]
            if is_link_relative(link['href']):
                link['href'] = self.domain + link['href']

    def _visit_page(self, page_url: str) -> None:
        """
        Processes a single page during the DFS scraping procedure.

        :param page_url: URL to the page.
        """
        print("Visiting %s; queued elements %d; %d on queue" % (page_url, len(self.visited_or_queued), len(self.queue)))

        # Parses the webpage and fetches the list of links.
        parser = ArticleParser()
        try:
            with urllib.request.urlopen(page_url) as response:
                html = response.read()
        except urllib.error.HTTPError:
            print("404")
            return

        parser.feed(str(html))
        print(parser.get_article_text())

        # Filters the links to be followed.
        links = parser.get_links()
        for link in links:
            self._preprocess_link(link)
        links_to_follow = list(filter(self.follow_link, links))
        for link in links_to_follow:
            # If link is to be followed, it must have 'href' attribute.
            assert 'href' in link
            if link['href'] in self.visited_or_queued:
                # Link has already been visited, there is a cycle in the link graph.
                continue
            # Appends the link url to the end of the queue.
            self.queue.append(link['href'])
            self.visited_or_queued.add(link['href'])

    def run(self):
        while self.queue:
            # Pops the first webpage from the queue.
            page = self.queue[0]
            self.queue = self.queue[1:]

            self._visit_page(page_url=page)
