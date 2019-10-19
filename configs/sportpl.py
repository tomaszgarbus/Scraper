from bs4 import BeautifulSoup
from lxml.html import document_fromstring
from typing import Optional

from article import Article
from configs.scraper_config import ScraperConfig


class SportPlScraperConfig(ScraperConfig):

    def __init__(self):
        super(SportPlScraperConfig, self).__init__()

    def home(self) -> str:
        return 'http://www.sport.pl/pilka'

    def domain(self) -> str:
        return 'http://www.sport.pl'

    def state_cache_fname(self) -> str:
        return 'sport_pl_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return (link.startswith('http://www.sport.pl/pilka') and
                'pilka/2' not in link)

    def _sportpl_remove_scripts(self, soup: BeautifulSoup) -> None:
        """
        Removes all <script> tags.
        :param soup: A BeautifulSoup representation of the article.
        """
        for tag in soup.findChildren():
            if tag.name == 'script':
                tag.extract()
            else:
                self._sportpl_remove_scripts(tag)

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_contents = soup.find_all(id='gazeta_article_body')
        for tag in art_contents:
            self._sportpl_remove_scripts(tag)
        if art_contents:
            article_text = document_fromstring(
                '\n'.join(list(map(str, art_contents)))).text_content()
            article_date_node = \
                (soup.find(class_='article_date') or
                 soup.find(id='gazeta_article_date'))
            article_date = ('' if not article_date_node else
                            article_date_node.time['datetime'])
            return Article(title=soup.title.text,
                           datetime=article_date,
                           text=article_text,
                           source_url=source_url,
                           raw_html=str(soup))
        return None
