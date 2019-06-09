from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig


class PilkaNoznaPlScraperConfig(ScraperConfig):
    def __init__(self):
        super(PilkaNoznaPlScraperConfig, self).__init__()

    def home(self) -> str:
        return 'http://www.pilkanozna.pl'

    def domain(self) -> str:
        return 'http://www.pilkanozna.pl'

    def state_cache_fname(self) -> str:
        return 'pilkanozna_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.domain())

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_contents = soup.find_all(class_='contentpaneopen')

