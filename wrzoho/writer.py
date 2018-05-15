import csv
import json
import jsontangle



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

def main():
    pass

