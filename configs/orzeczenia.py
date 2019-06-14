import time

import re
import subprocess
from bs4 import BeautifulSoup
from lxml.html import document_fromstring
from selenium import webdriver
from typing import Optional, List

from article import Article
from configs.scraper_config import ScraperConfig
import random


class NordVPNHelper:
    """
    This class encapsulates a bunch of utils for NordVPN. VPN is helpful for
    scraping orzeczenia.nsa.gov.pl since the website has some weird techniques
    preventing large traffic. For instance, it is capable of detecting TOR.

    Borrowed from https://github.com/Tesla-Nikola-2012/NordVPN_Randomizer.
    """
    CITIES = ['Tirana', 'Tallinn', 'Riga', 'Ljubljana', 'Buenos_Aires',
              'Helsinki', 'Steinsel', 'Johannesburg', 'Adelaide', 'Brisbane',
              'Melbourne', 'Perth', 'Sydney', 'Paris', 'Kuala_Lumpur', 'Seoul',
              'Vienna', 'Tbilisi', 'Mexico', 'Madrid', 'Brussels', 'Berlin',
              'Frankfurt', 'Chisinau', 'Stockholm', 'Sarajevo', 'Athens',
              'Amsterdam', 'Zurich', 'San_Paulo', 'Hong_Kong', 'Auckland',
              'Taipei', 'Sofia', 'Budapest', 'Skopje', 'Bangkok', 'Montreal',
              'Toronto', 'Vancouver', 'Reykjavik', 'Oslo', 'Istanbul',
              'Santiago', 'Chennai', 'Mumbai', 'Warsaw', 'Kiev', 'San_Jose',
              'Jakarta', 'Lisbon', 'London', 'Manchester', 'Zagreb', 'Dublin',
              'Bucharest', 'Atlanta', 'Chicago', 'Jackson', 'Louisville',
              'Minneapolis', 'Phoenix', 'San_Francisco', 'Buffalo', 'Dallas',
              'Las_Vegas', 'Manassas', 'New_Orleans', 'Saint_Louis', 'Seattle',
              'Charlotte', 'Denver', 'Los_Angeles', 'Miami', 'New_York',
              'Salt_Lake_City', 'Nicosia', 'Tel_Aviv', 'Belgrad', 'Hanoi',
              'Prague', 'Milan', 'Singapore', 'Copenhagen', 'Tokyo',
              'Bratislava']

    def __init__(self):
        self.countries = self.list_countries()

    def connect_to_random_city(self) -> None:
        """
        Connects to random city from all available cities. It would be wiser to
        select a specific server, but it seems command-line nordvpn app does not
        have this functionality.
        """
        subprocess.call(["nordvpn", "disconnect"])
        subprocess.call(["nordvpn", "connect", random.choice(self.CITIES)])
        self.display_status()

    @staticmethod
    def display_status() -> None:
        """
        Runs a status check on NordVPN and displays the output to stdout.
        """
        nord_output = subprocess.Popen(["nordvpn", "status"],
                                       stdout=subprocess.PIPE)
        status = re.split("[\r \n :]",
                          nord_output.communicate()[0].decode("utf-8"))[-2]
        print(status)

    @staticmethod
    def list_countries() -> List[str]:
        """
        Returns a list of the current countries with available servers for your
        NordVPN account.
        """
        nord_output = subprocess.Popen(["nordvpn", "countries"],
                                       stdout=subprocess.PIPE)
        countries = re.split("[\t \n]",
                             nord_output.communicate()[0].decode("utf-8"))

        while "" in countries:
            countries.remove("")
        countries.remove("\r-\r")
        for i, c in enumerate(countries):
            if c.startswith('\r'):
                countries[i] = c[1:]

        return countries

    @staticmethod
    def list_cities_for_country(country: str) -> List[str]:
        """
        Lists cities
        :param country: Selected country.
        :return: List of available cities in |country|.
        """
        nord_output = subprocess.Popen(["nordvpn", "cities", country],
                                       stdout=subprocess.PIPE)
        cities = re.split("[\t \n]",
                          nord_output.communicate()[0].decode("utf-8"))

        while "" in cities:
            cities.remove("")
        cities.remove("\r-\r")
        for i,c in enumerate(cities):
            if c.startswith('\r'):
                cities[i] = c[1:]

        return cities


class OrzeczeniaScraperConfig(ScraperConfig):
    # This constant determines the number of calls to |fetch_page| before VPN
    # should connect to another random server.
    REFRESH_VPN = 10

    # Time to sleep between GET requests in order to not get banned.
    TIME_BETWEEN_GET = 3

    def __init__(self):
        super(OrzeczeniaScraperConfig, self).__init__()
        # Initializes the PhantomJS browser and sets its timeout.
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(self.TIME_BETWEEN_GET)
        self.browser.set_page_load_timeout(self.TIME_BETWEEN_GET)
        self.nord_vpn_helper = NordVPNHelper()
        self.fetch_page_count = 0

    def home(self) -> str:
        return 'http://orzeczenia.nsa.gov.pl/cbo/find?p=1'

    def domain(self) -> str:
        return 'http://orzeczenia.nsa.gov.pl'

    def state_cache_fname(self) -> str:
        return 'orzeczenia_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return ((link.startswith('http://orzeczenia.nsa.gov.pl/cbo/find?p=') or
                link.startswith('http://orzeczenia.nsa.gov.pl/doc/'))
                and '.rtf' not in link)

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        art_content = '\n'.join(map(str,
                                    soup.find_all(
                                        class_='info-list-value-uzasadnienie'
                                    )))
        if art_content:
            article_text = document_fromstring(str(art_content)).text_content()
            article_title = soup.find(id='warunek').p.span.text
            return Article(title=article_title,
                           text=article_text,
                           source_url=source_url,
                           raw_html=str(soup),
                           datetime='')
        else:
            return None

    def fetch_page(self, page_url) -> str:
        self.fetch_page_count += 1
        if self.fetch_page_count % self.REFRESH_VPN == 0:
            self.nord_vpn_helper.connect_to_random_city()
        time.sleep(self.TIME_BETWEEN_GET)
        self.browser.get(page_url)
        html = self.browser.page_source
        # with urllib.request.urlopen(page_url) as response:
        #     html = response.read()
        return html
