from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig
from lxml.html import document_fromstring


class OrzeczeniaScraperConfig(ScraperConfig):

    def __init__(self):
        super(OrzeczeniaScraperConfig, self).__init__()

    def home(self) -> str:
        return 'http://orzeczenia.nsa.gov.pl/cbo/find?p=1'

    def domain(self) -> str:
        return 'http://orzeczenia.nsa.gov.pl'

    def state_cache_fname(self) -> str:
        return 'orzeczenia_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return (link.startswith('http://orzeczenia.nsa.gov.pl/cbo/find?p=') or
                link.startswith('http://orzeczenia.nsa.gov.pl/doc/'))

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_content = soup.find(class_='info-list-value-uzasadnienie')
        if art_content:
            article_text = document_fromstring(str(art_content)).text_content()
            article_title = soup.find(id='warunek').p.span.text
            return Article(title=article_title,
                           text=article_text,
                           source_url=source_url,
                           raw_html=str(soup),
                           datetime=None)
        else:
            return None