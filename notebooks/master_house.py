# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: soko
#     language: python
#     name: soko
# ---
import os
import datetime

import pandas as pd
import numpy as np

houses = pd.read_csv('../data/zillow_analysis.csv')

places = pd.read_csv('../data/niche_analysis.csv')

places = places.rename({'Name': 'city', 'State': 'state_long'}, axis=1)

master = pd.merge(houses, places, on=['city','state_long'], how='left')

# # Analysis

master['price_per_sq'] = master['price']/master['size']

# # Ordering - We want to keep the order of houses - to see what's been added

initial_ordering = pd.read_csv('../data/initial_ordering.csv')

master = pd.merge(master, initial_ordering, on='full_address',how='left')

master = master.sort_values('No').reset_index(drop=True)

master = master.reset_index().drop('No', axis=1)

master = master.rename({'index': 'No'}, axis=1)

master[['No', 'full_address']].to_csv('../data/initial_ordering.csv', index='False')

# # Google API

# ### Load

commute = pd.read_csv('../data/commute_times.csv')

master = pd.merge(master, commute, on='full_address', how='left')

# ### Run new

google_api_key = os.getenv('google_api_key','')

assert google_api_key != ''

gmaps = googlemaps.Client(key=google_api_key)

limit = 25

mon_morning_arrival = datetime.datetime(year=2023, month=9, day=18, hour=10, minute=0)
sat_morning_dept = datetime.datetime(year=2023, month=9, day=16, hour=10, minute=0)

origins = ['Pennsylvania Station']
destinations = master.loc[master['distance_value'].isna()]['full_address'].tolist()


def get_distances(origins, destinations, arrival=None, departure=None, max_req=10):
    dest_idx = 0
    req_count = 0
    distances = list()

    if arrival is not None and departure is not None:
        raise RuntimeError('Use either arrival or departuere')

    while dest_idx < len(destinations) and req_count < max_req:
        next_idx = min(len(destinations), dest_idx+limit)

        cur_destinations = destinations[dest_idx:next_idx]

        cur_distances = gmaps.distance_matrix(
            origins=origins,
            destinations=cur_destinations,
            arrival_time=arrival,
            departure_time=departure,
        )

        distances.append(cur_distances)
        dest_idx = next_idx
        req_count += 1
    return distances


destinations

weekend_commute = None
if len(destinations) > 0:
    print(f'Finding {len(destinations)}!')
    weekend_commute = get_distances(origins, destinations, departure=sat_morning_dept)

if len(destinations) > 0 and weekend_commute:

    addresses = list()

    duration_text = list()
    duration_value = list()

    duration_in_traffic_text = list()
    duration_in_traffic_value = list()

    distance_text = list()
    distance_value = list()

    for req in weekend_commute:
        cur_addresses = req['destination_addresses']
        addresses.extend(cur_addresses)
        for addr_idx in range(0, len(cur_addresses)):

            duration_text.append(req['rows'][0]['elements'][addr_idx]['duration']['text'])
            duration_value.append(req['rows'][0]['elements'][addr_idx]['duration']['value'])

            duration_in_traffic_text.append(req['rows'][0]['elements'][addr_idx]['duration_in_traffic']['text'])
            duration_in_traffic_value.append(req['rows'][0]['elements'][addr_idx]['duration_in_traffic']['value'])

            distance_text.append(req['rows'][0]['elements'][addr_idx]['distance']['text'])
            distance_value.append(req['rows'][0]['elements'][addr_idx]['distance']['value'])

    new_commute = pd.DataFrame([
        destinations,
        addresses,
        duration_text,
        duration_value,
        duration_in_traffic_text,
        duration_in_traffic_value,
        distance_text,
        distance_value
        ]
    ).T

    new_commute.columns=[
            'full_address',
            'found_addresses',
            'duration_text',
            'duration_value',
            'duration_in_traffic_text',
            'duration_in_traffic_value',
            'distance_text',
            'distance_value'
        ]

    commute = pd.concat([commute, new_commute])
    commute.to_csv('../data/commute_times.csv', index=False)

# # Saving

master.to_csv('../data/master_houses.csv', index=False)

master.tail(50)
