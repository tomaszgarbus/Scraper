from bs4 import BeautifulSoup
from lxml.html import document_fromstring
from typing import Optional

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
        return link.startswith(self.domain()) and 'Reklama' not in link

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_contents = soup.find_all(class_='contentpaneopen')
        if art_contents:
            article_text = document_fromstring(
                '\n'.join(list(map(str, art_contents)))).text_content()
            article_title = soup.find(class_='contentpagetitle').text
            article_date = soup.find(class_='createdate').text

            return Article(article_title, article_date, article_text,
                           source_url)

        return None

