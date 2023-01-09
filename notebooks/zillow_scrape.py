# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: fin2
#     language: python
#     name: fin2
# ---

from lxml import html
import requests as r
from pathlib import Path
import pandas as pd


# # Load and Parse Zillow

def load_page(fp):
    with open(fp, "r") as f:
        page = f.read()
    return html.fromstring(page)


def parse(page): 
    place = dict()
    
    # Summary 
    summary = page.xpath("//div[@class='summary-container']")[0]
    place['full_address'] = summary.xpath('//h1')[0].text_content().replace('\xa0', ' ')
    place['city'] = place['full_address'].split(', ')[1]
    place['state'] = place['full_address'].split(', ')[2][:2]
    place['price'] = page.xpath("//span[@data-testid='price']")[0].text_content()
    place['beds'] = page.xpath("//span[@data-testid='bed-bath-item']")[0].text_content()
    place['baths'] = page.xpath("//span[@data-testid='bed-bath-item']")[1].text_content()
    place['size'] = page.xpath("//span[@data-testid='bed-bath-item']")[2].text_content()
    
    # Data View 
    overview = page.xpath('//div[@class="data-view-container"]')[0]
    overview_summary = overview.xpath(
        "//ul[@class='zsg-tooltip-viewport']")[
        0].getchildren()[0].getchildren()[0].getchildren()[0].getchildren()[1].getchildren()
    place['built'] = overview_summary[1].getchildren()[2].text_content()
    place['heating'] = overview_summary[2].getchildren()[2].text_content()
    place['cooling'] = overview_summary[3].getchildren()[2].text_content()
    place['parking'] = overview_summary[4].getchildren()[2].text_content()
    place['lot'] = overview_summary[5].getchildren()[2].text_content()

    return place


save_path = Path('/Users/avogardo/Downloads/')

path = Path(save_path/Path('10 Laurel Lane, Huguenot, NY 12746 _ MLS #H6220082 _ Zillow.html'))

page = load_page(path)

parse(page)

places = list()
for fp in save_path.iterdir():
    if fp.suffix != '.html':
        continue
    try:
        page = load_page(fp)
        place = parse(page)
        places.append(place)
    except Exception as e:
        print('Not readable:', fp)

places_df = pd.DataFrame(places)

# places_df.duplicated('Name')

places_df.to_csv('../data/zillow_analysis.csv', index=False)

places_df


