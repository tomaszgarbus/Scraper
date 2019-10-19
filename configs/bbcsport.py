import re
from typing import Optional

from bs4 import BeautifulSoup
from lxml.html import document_fromstring

from article import Article
from configs.scraper_config import ScraperConfig


class BBCSportScraperConfig(ScraperConfig):
    def __init__(self):
        super(BBCSportScraperConfig, self).__init__()

    def home(self) -> str:
        return 'https://www.bbc.com/sport/football'

    def domain(self) -> str:
        return 'https://www.bbc.com'

    def state_cache_fname(self) -> str:
        return 'bbc_sport_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.home())

    @staticmethod
    def _remove_clutter_from_text(text: str) -> str:
        media_playback = 'Media playback is not supported on this device'
        text = re.sub(media_playback, '', text)
        return text

    @staticmethod
    def _extract_date(soup: BeautifulSoup) -> str:
        datetime = soup.find(
            class_='component component--default story').find('time')
        if datetime is not None and datetime.has_attr('data-timestamp'):
            datetime = datetime['data-timestamp']
        else:
            datetime = ''
        return datetime

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        story_body = soup.find(id='story-body')
        art_contents = story_body.find_all('p') if story_body else None
        if art_contents:
            text = document_fromstring(
                '\n'.join(list(map(str, art_contents)))
            ).text_content()
            text = self._remove_clutter_from_text(text)
            title_node = soup.find(class_='story-headline')
            if not title_node:
                return None
            title = title_node.text
            datetime = self._extract_date(soup)
            source_url = source_url
            raw_html = str(soup)
            return Article(title, datetime, text, source_url, raw_html)
        else:
            return None
