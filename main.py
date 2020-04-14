"""
Debugging.
"""
import argparse
import os

from configs.bbcsport import BBCSportScraperConfig
from configs.football import FootballCoUkScraperConfig
from configs.interiasport import InteriaSportScraperConfig
from configs.orzeczenia import OrzeczeniaScraperConfig
from configs.pap import PAPScraperConfig
from configs.pilkanoznapl import PilkaNoznaPlScraperConfig
from configs.sportonetpl import SportOnetPlScraperConfig
from configs.sportpl import SportPlScraperConfig
from scraper import ArticlesScraper

configs_mapping = {
    'sportpl': SportPlScraperConfig,
    'pilkanozna': PilkaNoznaPlScraperConfig,
    'orzeczenia': OrzeczeniaScraperConfig,
    'bbcsport': BBCSportScraperConfig,
    'pap': PAPScraperConfig,
    'interiasport': InteriaSportScraperConfig,
    'football': FootballCoUkScraperConfig,
    'sportonetpl': SportOnetPlScraperConfig,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraper TODO description.')
    parser.add_argument('-c', action='store', required=True, type=str, help='name of the config',
                        choices=configs_mapping.keys())
    parser.add_argument('-o', action='store', help='output directory', required=False, type=str)
    parser.add_argument('-r', action='store', help='raw html output directory', required=False, type=str)
    args = parser.parse_args()
    output_dir = args.o
    raw_html_dir = args.r
    config_name = args.c

    conf = configs_mapping[config_name]
    scraper = ArticlesScraper(conf())
    try:
        for article in scraper.run():
            print(article)
            if output_dir:
                pathdir = os.path.join(output_dir, article.nuid)
                os.makedirs(pathdir, exist_ok=True)
                fname = str(len(os.listdir(pathdir)))
                fpath = os.path.join(pathdir, fname)
                with open(fpath, 'w+') as file:
                    file.write(str(article))
            if raw_html_dir:
                pathdir = os.path.join(raw_html_dir, article.nuid)
                os.makedirs(pathdir, exist_ok=True)
                fname = str(len(os.listdir(pathdir)))
                fpath = os.path.join(pathdir, fname)
                with open(fpath, 'w+') as file:
                    file.write(article.raw_html)
            if (scraper.state.articles_found > 0 and
                    scraper.state.articles_found % 100 == 0):
                scraper.checkpoint()
    except KeyboardInterrupt:
        scraper.checkpoint()
