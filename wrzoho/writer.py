import csv
import json
import re
import jsontangle
from itertools import zip_longest, takewhile
import logging
import sys
import keboola
from pathlib import Path
import voluptuous as vp
from wrzoho.client import ZohoCrmClient

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
        yield from _do_delete(client, serialized_rows, module=module)
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
        logger.info("Chunk processed %s", json_response)
        yield json_response

def _do_delete(client, input_rows, module):
    """

    """
    # input rows is  a list of dicts [{'id': '1234'}, {'id': '5661'}]
    # we need chunk_of_ids to be [1234, 5661, ...]
    for chunk_of_ids in chunk_input_rows(
            (row['id'] for row in input_rows),
            n=100):
        logger.debug("Processing chunk")
        json_response = client.generic_delete(module=module, ids=chunk_of_ids)
        yield json_response

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

def validate_params(raw):
    schema = vp.Schema({
        vp.Optional("debug"): vp.Coerce(bool),
        "redirect_uri": str,
        "client_id": str,
        "#clinet_secret": str,
        "#refresh_token": str,
        "base_url": str,
        "base_tokens_url": str
    })

    return schema(raw)

def main(datadir):
    intables = Path(datadir) / 'in/tables'
    params = validate_params(keboola.docker.Config(datadir).get_parameters())
    if params.get('debug'):
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    _main(intables, params)


def _main(intables, params):
    credentials = {
        "refresh_token": params['#refresh_token'],
        "client_id": params['client_id'],
        "client_secret": params['#client_secret'],
        "redirect_uri": params['redirect_uri'],
        "base_url": params['base_url'],
        "base_tokens_url": params['base_tokens_url']
    }

    client = ZohoCrmClient(**credentials)
    for csv_path in intables.glob('*.csv'):
        with client:
            batch_results = parse_input_do_action(csv_path, client)
            processed = 0
            for batch in batch_results:
                processed += len(batch["data"])
                # we need to consume the generator!
                logger.info("Processed %s records", processed)
