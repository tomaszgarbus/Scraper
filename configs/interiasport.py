import re
from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig

# Substrings to remove from the text.
BLACKLIST = [
    'Odtwarzacz wideo wymaga uruchomienia obsługi JavaScript w przeglądarce.',
    'Wideo',
    'Zdjęcie',
    '//]]',
]
JS_PREF = [
    'var', '$', 'window.', 'if', 'else', '}', 'return'
]
JS_SUB = [
    '.style.', ' = ', '@media', 'Criteo', 'INTERIA.TV', 'player',
    'function', 'zoneid', 'containerid', 'false', 'true'
]
JS_SUF = [
    ';', '{'
]


class InteriaSportScraperConfig(ScraperConfig):
    def __init__(self):
        super(InteriaSportScraperConfig, self).__init__()

    def home(self) -> str:
        return 'https://sport.interia.pl'

    def domain(self) -> str:
        return 'https://sport.interia.pl'

    def state_cache_fname(self) -> str:
        return 'interiasport_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.home())

    def _is_line_js(self, line: str) -> bool:
        """
        A very simple heuristic determining whether the given line of text is
        JavaScript code.
        """
        for pref in JS_PREF:
            if line.strip().startswith(pref):
                return True
        for sub in JS_SUB:
            if sub in line:
                return True
        for suf in JS_SUF:
            if line.strip().endswith(suf):
                return True
        return False

    def _cleanup(self, text: str) -> str:
        for elem in BLACKLIST:
            text = re.sub(elem, '', text)
        lines = text.split('\n')
        lines = list(filter(lambda l: l.strip() != '', lines))
        lines = list(filter(lambda l: not self._is_line_js(l), lines))
        text = '\n'.join(lines)
        return text

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        title_node = soup.find('title')
        if title_node is None:
            return None
        title = title_node.text
        art_container = soup.find(class_='article-container')
        if art_container is None:
            return None
        article_date_node = art_container.find(class_='article-date')
        if article_date_node is None:
            return None
        datetime = art_container.find('meta').attrs['content']
        art_lead = soup.find(class_='article-lead')
        if art_lead is None:
            return None
        art_body = soup.find(class_='article-body')
        if art_body is None:
            return None
        text = art_lead.text + art_body.text
        text = self._cleanup(text)
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)

