import os
import datetime
import requests
import pytest

from wrzoho.client import BaseZohoCrmClient, ZohoCrmClient

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
    # because we have a refresh token set it's automatic

    assert client.access_token is not None
    assert client._access_token is not None
    assert 'Authorization' in client.headers



def test_upserting_and_deleting_contact(credentials):
    client = ZohoCrmClient(**credentials)
    data = {
        "data": [
            {
                "First_Name": "Keboola Writer",
                "Last_Name": "Can be deleted",
                "Description": "Upserted at {}".format(datetime.datetime.utcnow())
            }
        ]
    }
    created_resp = client.upsert_contact(payload=data, duplicate_check_fields='First_Name,Last_Name')
    contact = created_resp['data'][0]
    assert contact['status'] == 'success'

    contact_id = contact['details']['id']
    delete_resp = client.delete_contact(ids=[contact_id])
    assert delete_resp['data'][0]['status'] == 'success'
