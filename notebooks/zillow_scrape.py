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

import re
from pathlib import Path

import pandas as pd
from lxml import html

# # Load and Parse Zillow

state_mapping = {
    "NY": "New York",
    "NJ": "New Jersey",
    "PA": "Pennsylvania",
    "CT": "Connecticut",
}


def load_page(fp):
    with open(fp, "r") as f:
        page = f.read()
    return html.fromstring(page)


def parse(page):
    place = dict()

    # Summary
    summary = page.xpath("//div[@class='summary-container']")[0]
    place["full_address"] = summary.xpath("//h1")[0].text_content().replace("\xa0", " ")
    place["city"] = place["full_address"].split(", ")[1]
    place["state"] = place["full_address"].split(", ")[2][:2]
    place["state_long"] = state_mapping[place["state"]]
    place["price"] = page.xpath("//span[@data-testid='price']")[0].text_content()
    place["beds"] = page.xpath("//span[@data-testid='bed-bath-item']")[0].text_content()
    place["baths"] = page.xpath("//span[@data-testid='bed-bath-item']")[
        1
    ].text_content()
    place["size"] = page.xpath("//span[@data-testid='bed-bath-item']")[2].text_content()

    # Data View
    overview = page.xpath('//div[@class="data-view-container"]')[0]
    overview_summary = (
        overview.xpath("//ul[@class='zsg-tooltip-viewport']")[0]
        .getchildren()[0]
        .getchildren()[0]
        .getchildren()[0]
        .getchildren()[1]
        .getchildren()
    )
    place["built"] = overview_summary[1].getchildren()[2].text_content()
    place["heating"] = overview_summary[2].getchildren()[2].text_content()
    place["cooling"] = overview_summary[3].getchildren()[2].text_content()
    place["parking"] = overview_summary[4].getchildren()[2].text_content()
    place["lot"] = overview_summary[5].getchildren()[2].text_content()
    does_include_sqft = len(re.findall(r" sqft", place["lot"].lower())) > 0
    does_include_acres = len(re.findall(r" acres", place["lot"].lower())) > 0

    if not does_include_sqft and not does_include_acres:
        place["lot"] = ""

    return place


save_path = Path("../data/raw/zillow/")

places = list()
for fp in save_path.iterdir():
    if fp.suffix != ".html":
        continue
    try:
        page = load_page(fp)
        place = parse(page)
        places.append(place)
    except Exception as e:
        print("Not readable:", fp)
        print(e)

places_df = pd.DataFrame(places)

places_df

places_df["size"] = places_df["size"].apply(
    lambda x: x.replace(" sqft", "").replace(",", "").replace("--", "")
)
places_df["price"] = places_df["price"].apply(
    lambda x: x.replace("$", "").replace(",", "")
)
places_df["size"] = places_df["size"].apply(
    lambda x: x.replace(" sqft", "").replace(",", "").replace("--", "")
)
places_df["beds"] = places_df["beds"].apply(lambda x: x.replace(" bd", ""))
places_df["baths"] = places_df["baths"].apply(lambda x: x.replace(" ba", ""))
places_df["baths"] = places_df["baths"].apply(lambda x: x.replace(" ba", ""))
places_df["built"] = places_df["built"].apply(lambda x: x.replace("Built in ", ""))
places_df["lot"] = places_df["lot"].apply(lambda x: x.replace(" Acres", ""))
places_df["city"] = places_df["city"].apply(
    lambda x: x.replace(" Township", "").replace(" Boro", "").replace(" Twp.", "")
)

is_sqft_value = places_df["lot"].apply(lambda x: len(re.findall(" sqft", x)) > 0)

places_df.loc[is_sqft_value, "lot"] = (
    places_df.loc[is_sqft_value, "lot"]
    .apply(lambda x: x.replace(" sqft", "").replace(",", ""))
    .astype(int)
    / 43560
)

places_df

# places_df.duplicated('Name')

places_df.to_csv("../data/zillow_analysis.csv", index=False)
