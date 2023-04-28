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
from pathlib import Path
import pandas as pd


# # Load and Parse Niche

def load_page(fp):
    with open(fp, "r") as f:
        page = f.read()
    return html.fromstring(page)


def parse_scalar(scalar):
    sc_elements = scalar.getchildren()
    parsed_sc = dict()
    for element in sc_elements:
        if element.items()[0][1] == 'scalar__label':
            parsed_sc['name'] = element.getchildren()[0].text
        elif element.items()[0][1] == 'scalar__value':
            parsed_sc['value'] = element.getchildren()[0].text
    return parsed_sc


def find_scalar(name, page):
    scalars = page.xpath("//div[@class='scalar']")
    for scalar in scalars:
        parsed_sc = parse_scalar(scalar)
        if parsed_sc['name'] == name:
            return parsed_sc
    else:
        raise RuntimeError(f'Scalar {name} Not Found')


def parse_niche(page):
    place = dict()

    # Name
    place['Name'] = page.xpath("//h1[@class='postcard__title']")[0].text_content().replace(' Township', '').replace(' Boro', '')
    place['State'] = page.xpath("//ul[@class='profile-breadcrumbs']")[0].getchildren()[0].text_content()
    place['County'] = page.xpath("//ul[@class='profile-breadcrumbs']")[0].getchildren()[1].text_content()

    # Scalars
    scalars = ['Population', 'Area Feel']
    for scalar in scalars:
        parsed_scalar = find_scalar(scalar, page)
        place[parsed_scalar['name']] = parsed_scalar['value']

    # Scores
    report_card = page.get_element_by_id('report-card').getchildren()[1].getchildren()[0].getchildren()[0]

    overall_score_card = report_card.getchildren()[0].xpath("//div[@class='overall-grade__niche-grade']")[0].getchildren()
    individual_score_card = report_card.getchildren()[1].xpath("//ol[@class='ordered__list__bucket']")[0].getchildren()

    overall_score = overall_score_card[0].text_content().split('grade\xa0')[1]

    individual_scores = dict()
    individual_scores['Overall Score'] = overall_score

    for score in individual_score_card:
        score = score.text_content().split('grade\xa0')
        individual_scores[score[0]] = score[1]
    individual_scores

    for score_name in individual_scores:
        individual_scores[score_name] = individual_scores[score_name].replace(' minus','-')
        individual_scores[score_name] = individual_scores[score_name].replace(' plus','+')
    place.update(individual_scores)
    return place


save_path = Path('../data/raw/niche/')

places = list()
for fp in save_path.iterdir():
    if fp.suffix != '.html':
        continue
    try:
        page = load_page(fp)
        place = parse_niche(page)
        places.append(place)
    except Exception as e:
        print('Not readable:', fp)
        print(e)

places_df = pd.DataFrame(places)

places_df.duplicated('Name').sum()

places_df.to_csv('../data/niche_analysis.csv', index=False)
