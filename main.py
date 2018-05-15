from wrzoho.writer import main
import sys
import requests
import logging
import os

if __name__ == "__main__":
    try:
        main(datadir=os.getenv("KBC_DATADIR"))
    except (ValueError, KeyError) as err:
        logging.error(err)
    except requests.HTTPError as err:
        logging.error("{}: {}".format(err, err.response.text))
    except:
        logging.exception("Internal error")
