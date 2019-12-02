import re
from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig

# Substrings to remove from the text.
BLACKLIST = [
    'REKLAMA',
    'PODZIEL SIĘ',
    'KOPIUJ LINK',
    'Zobacz zdjęcia',
    'FAKT24.PL',
    'Sport',
    'Piłka nożna',
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


class FaktSportScraperConfig(ScraperConfig):
    def __init__(self):
        super(FaktSportScraperConfig, self).__init__()

    def home(self) -> str:
        return 'https://www.fakt.pl/sport/pilka-nozna'

    def domain(self) -> str:
        return 'https://www.fakt.pl'

    def state_cache_fname(self) -> str:
        return 'faktsport_state_cache'

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
        title = soup.find('title').text
        datetime_node = soup.find('time')
        if datetime_node is None:
            return None
        datetime = datetime_node.text
        art_node = soup.find('article')
        if art_node is None:
            return None
        text = art_node.text
        text = self._cleanup(text)
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)

