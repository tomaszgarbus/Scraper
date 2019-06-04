import urllib.request
from html.parser import HTMLParser
from typing import List



class ArticlesScraper:
    """
    A scraper for articles. The goal is for this scraper to be as universal as possible.
    """
    def __init__(self,
                 home: str,
                 limit: int):
        """
        A constructor for a scraper object.
        :param home: The starting page.
        :param limit: Maximum number of visited web pages.
        """
        super(ArticlesScraper, self).__init__()
        self.home = home
        self.limit = limit
        # Creates a queue of web pages to visit.
        self.queue: List[str] = [self.home]

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            print("Encountered a start tag:", tag, attrs)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        super().handle_data(data)
        pass

    def run(self):
        with urllib.request.urlopen(self.home) as response:
            self.html = response.read()
        self.feed(str(self.html))