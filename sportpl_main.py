"""
Debugging.
"""
import argparse
import os

from sportpl_scraper import SportPlArticlesScraper, sportpl_follow_link

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes sport.pl/pilka.')
    parser.add_argument('-o', action='store', required=False, type=str)
    args = parser.parse_args()
    output_dir = args.o

    scraper = SportPlArticlesScraper(home='http://www.sport.pl/pilka',
                                     domain='http://www.sport.pl',
                                     follow_link=sportpl_follow_link)
    for article in scraper.run():
        print(article)
        if output_dir:
            path = os.path.join(output_dir, article.datetime)
            with open(path, 'w+') as file:
                file.write(str(article))
