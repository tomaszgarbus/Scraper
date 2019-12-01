from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig


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

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        title = soup.find('title').text
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
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)

