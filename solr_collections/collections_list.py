"""
Lists BDR collection names and item counts from the public search API.
"""

import logging
import os
from pathlib import Path

import httpx
from columnar import columnar
from dotenv import load_dotenv

## the dotenv-directory is in the "stuff" directory.
DOTENV_PATH: Path = Path(__file__).resolve().parents[2] / 'dot_env_files' / 'solr_collections.env'

## load variables from script-specific dotenv file
load_dotenv(DOTENV_PATH)


BDR_API_URL: str = os.getenv('SC__BDR_API_URL', 'https://repository.library.brown.edu/api/search/')
COLLECTION_FIELD: str = os.getenv('SC__COLLECTION_FIELD', 'ir_collection_name')
LOGLEVEL: str = os.getenv('SC__LOGLEVEL', 'INFO')
REQUEST_TIMEOUT: float = float(os.getenv('SC__REQUEST_TIMEOUT', '30'))


## setup console logging
LOG_LEVELS: dict[str, int] = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
}
logging.basicConfig(level=LOG_LEVELS.get(LOGLEVEL, logging.INFO), format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)


def get_bdr_collections() -> dict[str, int]:
    """
    Gets a mapping of BDR collection names to item counts.

    Called by: main()
    """
    params = {
        'q': '*',
        'facet': 'on',
        'facet.field': COLLECTION_FIELD,
        'rows': 0,
    }
    log.debug('calling %s with params %s', BDR_API_URL, params)
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(BDR_API_URL, params=params)
    response.raise_for_status()
    response_json = response.json()
    facet_counts = response_json['facet_counts']['facet_fields'][COLLECTION_FIELD]
    collection_counts = dict(zip(facet_counts[::2], facet_counts[1::2], strict=True))
    return collection_counts


def print_collections_table(bdr_collections: dict[str, int]) -> None:
    """
    Prints a table of BDR collection names and item counts.

    Called by: main()
    """
    collections_table = [[key, value] for key, value in bdr_collections.items()]
    table_headers = ['collection', 'no. items']
    print(columnar(collections_table, headers=table_headers, no_borders=True))
    print(f'Total number of collections: {len(bdr_collections)}')


def main() -> None:
    """
    Gets and prints BDR collection counts.

    Called by: command line
    """
    bdr_collections = get_bdr_collections()
    print_collections_table(bdr_collections)


if __name__ == '__main__':
    main()
