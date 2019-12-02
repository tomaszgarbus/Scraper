import re
from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig

RM_EQU = []
RM_PREF = [
    'var', '$', 'window.', 'if', 'else', '}', 'return', '{'
]
RM_SUB = [
    'function', 'zoneid', 'containerid', 'text/javascript', 'adsbygoogle',
    'Source:'
]
RM_SUF = [
    ';', '{'
]


class FootballCoUkScraperConfig(ScraperConfig):
    def home(self) -> str:
        return 'http://www.football.co.uk'

    def domain(self) -> str:
        return 'http://www.football.co.uk'

    def state_cache_fname(self) -> str:
        return 'football_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.home())

    def _remove_line(self, line: str) -> bool:
        """
        Determines whether a line should be removed.
        """
        for elem in RM_EQU:
            if line.strip() == elem:
                return True
        for pref in RM_PREF:
            if line.strip().startswith(pref):
                return True
        for sub in RM_SUB:
            if sub in line:
                return True
        for suf in RM_SUF:
            if line.strip().endswith(suf):
                return True
        return False

    def _cleanup(self, text: str) -> str:
        lines = text.split('\n')
        lines = list(filter(lambda l: l.strip() != '', lines))
        lines = list(filter(lambda l: not self._remove_line(l), lines))
        text = '\n'.join(lines)
        return text

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        title = soup.find('title').text
        date_node = soup.find(id='author')
        if date_node is None:
            return None
        datetime = date_node.text.strip()
        text_node = soup.find(class_='article-content')
        if text_node is None:
            return None
        text = text_node.text
        text = self._cleanup(text)
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)
