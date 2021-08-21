"""
funcs.py

List of functions to be applied on the
raw data using a `Pipeline`.
"""

import os
import re
import requests
from pipeline import Pipeline

pipeline = Pipeline()
pipeline['core'] = Pipeline(seq_dump=True)


@pipeline.add_to('core', key='items', throw=True)
def convert_metadata(item):
    """
    The `metadata` (event['item']['metadata']) for an item
    consists of strings that look like this: "Creator:
    Robert Sargent". This function parses this data into
    a dictionary. If an item is missing any attribute it
    is discarded.
    """
    keys = [v.split(': ', 1) for v in item['metadata']]
    key_dict = {v[0]: v[1] for v in keys}
    item = {
        'id': item['id'],
        'image_url': item['image_url'],
        'title': key_dict['Title'],
        'description': item['description'],
        'location': key_dict.get('Location'),

    }
    return item


@pipeline.add_to('core')
def remove_small_events(event):
    """
    If an event does not have enough items, then it
    is not suitable for production.
    """
    if len(event['items']) > 10:
        return event


@pipeline.add_to('core')
def get_location(event):
    """
    Extracts `location` data and keeps only`
    events with it provided.
    """
    for item in event['items']:
        if item['location']:
            event['location'] = item['location']
            return event
    return None


@pipeline.add_to('core')
def filter_event_attrs(event):
    """
    Keeps only a select attributes from
    each event.
    """
    return {
        'id': event['id'],
        'title': event['title'],
        'date': event['date'],
        'location': event['location'],
        'description': event['description'],
        'items': event['items']
    }


@pipeline.add_to('core')
def convert_date(event):
    """
    Date is parsed from string to year.
    """
    event['date'] = int(re.match(r'.*([0-9]{4})', event['date']).group(1))
    return event


@pipeline.add_to('web')
def get_coordinates(event: dict):
    """
    Replaces `location` with its coordinates, which
    are fetched from Google Maps API.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    url = f'{api_url}{event["location"]}&key={api_key}'
    res = requests.get(url).json()['results'][0]
    event.pop("location")  # no longer needed
    event["Coords"] = res['geometry']['location']
    return event


@pipeline.add_to('web')
def download_images(event):
    """
    Downloads images from `image_url` into the
    images folder. Requires `curl`.
    """
    root = os.path.join('images', str(event['id']))
    os.makedirs(root, exist_ok=True)
    for idx, item in enumerate(event['items']):
        path = os.path.join(root, f"{idx:03d}.jpeg")
        command = ["curl", item['image_url'][2:], "--output", path, '&']
        os.popen(" ".join(command))
    return event


@pipeline.add_to('web', key='items')
def filter_item_attrs(item):
    """
    Keeps only select attributes from the `items`
    object.
    """
    return {
        'id': item['id'],
        'title': item['title'],
        'description': item['description']
    }
