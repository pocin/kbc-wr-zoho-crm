import os
import datetime
import pathlib
import requests
import logging
import pytest

import wrzoho

from wrzoho.client import BaseZohoCrmClient, ZohoCrmClient

@pytest.fixture(scope='module')
def credentials():
    return  {
    "refresh_token": os.environ['ZOHO_REFRESH_TOKEN'],
    "client_id": os.environ['ZOHO_CLIENT_ID'],
    "client_secret": os.environ['ZOHO_CLIENT_SECRET'],
    "redirect_uri": os.environ['ZOHO_REDIRECT_URI'],
    "base_url": os.environ['ZOHO_BASE_URL'],
    "base_tokens_url": os.environ['ZOHO_BASE_TOKENS_URL']
}

def test_getting_access_token(credentials):
    client = BaseZohoCrmClient(**credentials)
    # because we have a refresh token set it's automatic

    assert client.access_token is not None
    assert client._access_token is not None
    assert 'Authorization' in client.headers



def test_creating_and_deleting_contact(credentials):
    client = ZohoCrmClient(**credentials)
    message = "Created at {}Z".format(datetime.datetime.utcnow())
    data = {
        "data": [
            {
                "First_Name": "Keboola Writer",
                "Last_Name": "Can Be Deleted",
                "Description": message
            }
        ]
    }
    created_resp = client.create_contacts(payload=data)
    contact = created_resp['data'][0]
    assert contact['status'] == 'success'

    contact_id = contact['details']['id']
    delete_resp = client.delete_contacts(ids=[contact_id])
    assert delete_resp['data'][0]['status'] == 'success'

def test_make_api_calls_from_csv(tmpdir, credentials, caplog):
    client = ZohoCrmClient(**credentials)

    # create contact
    incsv = tmpdir.join("create_contacts.csv")
    incsv.write("""First_Name,Last_Name,Description
KBC Writer,Can Be Deleted,"Functional test @{}z""".format(datetime.datetime.utcnow()))

    incsv_path = pathlib.Path(incsv.strpath)
    create_logs = list(wrzoho.writer.parse_input_do_action(incsv_path, client))
    assert len(create_logs) == 1 # one batch worth of logs
    assert len(create_logs[0]['data']) == 1 # one record in first batch

    new_contact = create_logs[0]['data'][0]
    assert new_contact['status'] == 'success'
    new_contact_id = new_contact['details']['id']

    # update the contact
    update_csv = tmpdir.join("update_contacts.csv")
    desc = "Updated functional test @{}Z".format(datetime.datetime.utcnow())
    update_csv.write("""id,Description
{id_},{desc}""".format(id_=new_contact_id,
                       desc=desc))

    update_csv_path = pathlib.Path(update_csv.strpath)
    update_logs = list(wrzoho.writer.parse_input_do_action(update_csv_path, client))

    #      1 batch       data    #1st record
    updated_record = update_logs[0]['data'][0]
    assert updated_record['status'] == 'success'
    assert updated_record['message'] == 'record updated'

    # delete it
    delete_csv = tmpdir.join("delete_contacts.csv")
    delete_csv.write("""id
{}""".format(new_contact_id))
    delete_csv_path = pathlib.Path(delete_csv.strpath)
    delete_logs = list(wrzoho.writer.parse_input_do_action(delete_csv_path, client))

    deleted_record = delete_logs[0]['data'][0]

    assert deleted_record['status'] == 'success'
    assert deleted_record['message'] == 'record deleted'
