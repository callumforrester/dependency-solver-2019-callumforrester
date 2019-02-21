import json

from typing import Iterator, Dict


def load_json(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
