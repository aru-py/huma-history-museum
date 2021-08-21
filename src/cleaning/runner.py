"""
runner.py

Note
-----
The `web` pipeline must be run separately, since
it takes a long time and is error-prone. Only the
`core` pipeline is run here.
"""

import json
import pickle

from funcs import pipeline

from pathlib import Path

data_dir = Path('../../data/')

with open(data_dir / 'data_raw.pkl', 'rb') as p:
    data = pickle.load(p)

data = data['events']
data = pipeline['core'](data)

with open(data_dir / 'data_clean.json', 'w+') as f:
    json.dump(data, f)

print(pipeline['core'].loss)
