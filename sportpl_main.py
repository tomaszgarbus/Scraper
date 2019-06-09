"""
Debugging.
"""
import argparse
import os

from configs.sportpl import SportPlScraperConfig
from scraper import ArticlesScraper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes sport.pl/pilka.')
    parser.add_argument('-o', action='store', required=False, type=str)
    args = parser.parse_args()
    output_dir = args.o

    scraper = ArticlesScraper(SportPlScraperConfig())
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
