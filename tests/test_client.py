import os
import requests
import pytest

from wrzoho.client import BaseZohoCrmClient

@pytest.fixture(scope='module')
def credentials():
    return  {
    "refresh_token": os.environ['ZOHO_REFRESH_TOKEN'],
    "client_id": os.environ['ZOHO_CLIENT_ID'],
    "client_secret": os.environ['ZOHO_CLIENT_SECRET'],
    "redirect_uri": os.environ['ZOHO_REDIRECT_URI']
}

def test_getting_access_token(credentials):
    client = BaseZohoCrmClient(**credentials)

    assert client._access_token is None

    assert client.access_token is not None
    assert client._access_token is not None
    assert 'Authorization' in client.headers


