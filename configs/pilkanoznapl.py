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
        # If any of the below patterns occurs in the link, it is most likely
        # not an article.
        forbidden = ['Reklama', 'showResultsRank', 'showRanking', 'showMatrix',
                     'showClubInfo', 'showPlayer', 'showReport', 'Kontakt',
                     'Redakcja', 'Poll-results', 'Prenumerata']
        return (link.startswith(self.domain()) and 'Reklama' not in link
                and not list(filter(lambda substr: substr in link, forbidden)))

    @staticmethod
    def _remove_read_next(article_text: str) -> str:
        """
        In many articles there is an irrelevant headline followed by
        'Czytaj dalej', both in separate consecutive lines. This function
        removes both of those lines.
        :param article_text: The content of the article.
        :return: A subsequence of |article_text|.
        """
        pattern = 'Czytaj dalej...'
        split = article_text.split('\n')
        split = list(map(lambda s: s.strip(), split))
        try:
            idx = split.index(pattern)
            return '\n'.join(split[:idx - 1] + split[idx + 1:])
        except ValueError:
            # 'Czytaj dalej...' pattern not found in the article content.
            return article_text

    @staticmethod
    def _remove_substring_if_any(article_text: str, pattern: str) -> str:
        """
        Removes |pattern| from |article_text| if it occurs there.
        :param article_text: The content of the article.
        :param pattern: A pattern to seek and delete.
        :return: A subsequence of |article_text|, without |pattern|.
        """
        while pattern in article_text:
            idx = article_text.find(pattern)
            article_text = (article_text[:idx] +
                            article_text[idx + len(pattern) + 1:])
        return article_text

    @staticmethod
    def _remove_empty_lines(article_text: str) -> str:
        """
        Removes empty lines from the article content.
        :param article_text: Content of the article.
        :return: Content of the article minus empty lines.
        """
        return '\n'.join(
            filter(lambda s: s.strip() != '', article_text.split('\n')))

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_contents = soup.find_all(class_='contentpaneopen')
        art_contents = list(filter(
            lambda res: 
              res.find_next_sibling(class_='article_separator') is not None,
            art_contents
        ))
        if art_contents:
            # Extracts the article text, title and date.
            article_text: str = document_fromstring(
                '\n'.join(list(map(str, art_contents)))).text_content().strip()
            article_title = soup.find(class_='contentpagetitle').text.strip()
            article_date = soup.find(class_='createdate').text.strip()

            # Removes empty lines from the article content.
            article_text = self._remove_empty_lines(article_text)
            # Removes the duplicated article title from the article content.
            article_text = self._remove_substring_if_any(article_text,
                                                         article_title)
            # Does the same with the article date.
            article_text = self._remove_substring_if_any(article_text,
                                                         article_date)
            # Removes an irrelevant prefix of the article (an advertisement of
            # another article)
            if 'KLIKNIJ!' in article_text:
                article_text = \
                    article_text[
                        article_text.find('KLIKNIJ!') + len('KLIKNIJ!'):
                        ]
            # Removes an irrelevant suffix of the article content.
            if 'Facebook Social Comments' in article_text:
                article_text = article_text[:article_text.find(
                    'Facebook Social Comments'
                )]
            # Searches for 'Czytaj dalej...' interruption and removes it.
            article_text = self._remove_read_next(article_text)
            # Strips the whitespace once more.
            article_text = article_text.strip()

            return Article(article_title, article_date, article_text,
                           source_url)

        return None

