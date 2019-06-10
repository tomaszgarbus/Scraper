"""
Debugging.
"""
import argparse
import os

from configs.pilkanoznapl import PilkaNoznaPlScraperConfig
from configs.sportpl import SportPlScraperConfig
from configs.orzeczenia import OrzeczeniaScraperConfig
from scraper import ArticlesScraper

configs_mapping = {
    'sportpl': SportPlScraperConfig,
    'pilkanozna': PilkaNoznaPlScraperConfig,
    'orzeczenia': OrzeczeniaScraperConfig,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraper TODO description.')
    parser.add_argument('-c', action='store', required=True, type=str,
                        choices=configs_mapping.keys())
    parser.add_argument('-o', action='store', required=False, type=str)
    args = parser.parse_args()
    output_dir = args.o
    config_name = args.c

    conf = configs_mapping[config_name]
    scraper = ArticlesScraper(conf())
    try:
        for article in scraper.run():
            print(article)
            if output_dir:
                pathdir = os.path.join(output_dir, article.datetime)
                os.makedirs(pathdir, exist_ok=True)
                fname = str(len(os.listdir(pathdir)))
                fpath = os.path.join(pathdir, fname)
                with open(fpath, 'w+') as file:
                    file.write(str(article))
    except KeyboardInterrupt:
        scraper.checkpoint()
