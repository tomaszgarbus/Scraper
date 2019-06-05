import urllib.request
from html.parser import HTMLParser
from typing import List, Dict, Callable, Set


class ArticleParser(HTMLParser):
    def __init__(self):
        super(ArticleParser, self).__init__()
        self.links = []

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            # Converts the list of attributes to a dictionary.
            attrs_dict = {}
            for (k, v) in attrs:
                attrs_dict[k] = v
            # Appends the link to the list.
            self.links.append(attrs_dict)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        super().handle_data(data)
        pass

    def get_links(self) -> List[Dict[str, str]]:
        """
        Returns a list of links found in the article.
        :return: A list of dictionaries, where keys and values corresponds to the 'a' tag attributes.
        """
        return self.links


class ArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as possible.
    """
    def __init__(self,
                 home: str,
                 limit: int = -1,
                 follow_link: Callable[[Dict], bool] = (lambda _: True)):
        """
        A constructor for a scraper object.
        :param home: The starting page.
        :param limit: Maximum number of visited web pages. If set to -1, then there is no limit.
        :param follow_link: A function determining, whether to follow a link.
        """
        super(ArticlesScraper, self).__init__()

        self.home = home
        self.limit = limit
        self.follow_link = follow_link

        # Creates a queue of web pages URLs to visit.
        self.queue: List[str] = [self.home]
        # Creates a set of visited links.
        self.visited: Set[str] = set()

    def run(self):
        while self.queue:
            # Pops the first webpage from the queue.
            page = self.queue[0]
            self.queue = self.queue[1:]
            self.visited.add(page)

            print(page)

            # Parses the webpage and fetches the list of links.
            parser = ArticleParser()
            with urllib.request.urlopen(self.home) as response:
                self.html = response.read()
            parser.feed(str(self.html))

            # Filters the links to be followed.
            links_to_follow = list(filter(self.follow_link, parser.get_links()))
            for link in links_to_follow:
                # If link is to be followed, it must have 'href' attribute.
                assert 'href' in link
                if link['href'] in self.visited:
                    # Link has already been visited, there is a cycle in the link graph.
                    continue
                # Appends the link url to the end of the queue.
                self.queue.append(link['href'])
