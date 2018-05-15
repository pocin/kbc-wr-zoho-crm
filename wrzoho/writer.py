import csv
import json
import re
import jsontangle
from itertools import zip_longest, takewhile
import logging
import sys

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stdout))

AVAILABLE_MODULES = {"leads", "accounts", "contacts", "deals", "campaigns",
                     "cases", "solutions", "products", "vendors", "pricebooks",
                     "quotes", "salesorders", "purchaseorders", "invoices",
                     "custom", "notes"}


def parse_input_csv(path):
    """Serialize csv to json (handle nesting!)
    Args:
        path: /path/to/input.csv
    Returns:
        a generator yielding serialized rows

    Example:


    $ cat ./create_campaign.csv
    last_name,first_name,campaign_source__id
    Doe,Jane,42
    Doe,John,999
    Hoe,Mary,666
    $ python
    >>> from wrzoho.writer import parse_input_csv
    >>> expected = list(parse_input_csv('./create_campaign.csv'))
    >>> print(expected)
    [
        {"last_name":"Doe","first_name":"Jane","campaign_source":{"id":"42"}},
        {"last_name":"Doe","first_name":"John","campaign_source":{"id":"999"}},
        {"last_name":"Hoe","first_name":"Mary","campaign_source":{"id":"666"}}
    ]


    """
    with open(path) as fin:
        reader = csv.DictReader(fin)
        for line in reader:
            yield jsontangle.tangle(line)

def parse_input_do_action(path_csv, client):
    """ parse the input csv and use the rows as payload

    The action is decide from the name of the input csv

    Args:
        path_csv (pathlib.Path): path/to/input.csv
        clinet (wrzoho.client.ZHOCRMClient) instance
    """
    # update_contact
    action, module = decide_action_from_filename(path_csv)
    serialized_rows = parse_input_csv(path_csv)
    if action == "delete":
        yield from _do_delete(client, serialized_rows)
    else:
        yield from _do_update_create(client, serialized_rows, action=action, module=module)


def _do_update_create(client, input_rows, action, module):
    """

    """
    logger.info("Doing action '%s' on module '%s'", action, module)
    # the api call takes max 100 rows in one request

    for chunk in chunk_input_rows(input_rows, n=100):
        logger.info("Processing chunk")
        payload = {"data": list(chunk)}
        json_response = getattr(client, 'generic_' + action)(module=module, payload=payload)
        logger.info("Batch processed %s", json_response)
        yield json_response

def _do_delete(client, input_rows):
    """

    """
    raise NotImplementedError("TODO: need to pass the ids as params in querystring")

def chunk_input_rows(iterable, n=100):

    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    logger.debug("Chunking input rows for the api")
    args = [iter(iterable)] * n
    for chunk in zip_longest(*args):
        yield takewhile(lambda x: x is not None, chunk)


def decide_action_from_filename(path_csv):
    logging.debug("Figuring out what to do with csv '%s'", path_csv)
    action_module = path_csv.stem
    valid_fname_pattern = re.compile(r'^(?P<action>create|update|delete)_(?P<module>\w+)')
    parts = valid_fname_pattern.match(action_module)
    if not parts:
        raise ValueError(
            "Don't know what to do with {}, expecting "
            "{{create|update|delete}}_{{module_name}}.csv!".format(path_csv))

    action, module = parts.groups()
    if module not in AVAILABLE_MODULES:
        raise ValueError(
            "module name in the input csv must be one of "
            "'{}', not '{}'".format(AVAILABLE_MODULES, module))

    else:
        return action, module


def main():
    pass

