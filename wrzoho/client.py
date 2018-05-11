import requests
from urllib.parse import urljoin, urlsplit, parse_qsl
import logging

logger = logging.getLogger(__name__)


class BaseZohoCrmClient(requests.Session):
    def __init__(self,  redirect_uri, client_id, client_secret, refresh_token=None, base_url='https://www.zohoapis.com/crm/v2/'):
        super().__init__()
        self.redirect_uri = redirect_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._access_token = None
        self.base_url = base_url

        if refresh_token is not None:
            self.refresh_access_token()

    @property
    def access_token(self):
        if self._access_token is None:
            self.refresh_access_token()
        return self._access_token

    @access_token.setter
    def access_token(self, new_token):
        """Set access token + update auth headers"""
        logger.debug("Setting new access token")
        self._access_token = new_token

        logger.debug("Updating TTD-Auth header")
        self.headers.update({"Authorization": "Zoho-oauthtoken {}".format(new_token)})


    def authorization_url(self, scope='ZohoCRM.modules.ALL'):
        return ('https://accounts.zoho.com/oauth/v2/auth'
                '?scope={scope}'
                '&client_id={client_id}'
                '&response_type=code'
                '&access_type=offline'
                '&redirect_uri={redirect_uri}').format(
                    scope=scope,
                    client_id=self.client_id,
                    redirect_uri=self.redirect_uri)

    def convert_grant_token(self, grant_token=None, url_with_grant_token=None):

        token = grant_token or dict(parse_qsl(urlsplit(url_with_grant_token).query))['code']

        url = "https://accounts.zoho.com/oauth/v2/token"

        params = {
            "code": grant_token,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code"
        }

        resp = requests.post(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def refresh_access_token(self):

        logger.debug("Getting new access token")
        if self.refresh_token is None:
            raise ValueError(
                "refresh_token must be set before getting access tokens")

        url = "https://accounts.zoho.com/oauth/v2/token"
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        resp = self.post(url=url, params=params)
        resp.raise_for_status()
        try:
            self.access_token = resp.json()["access_token"]
        except KeyError:
            raise KeyError("{} doesn't contain access_token".format(resp.json()))


    def _build_url(self, endpoint):
        return urljoin(self.base_url, endpoint.lstrip("/"))

    def request(self, method, url, *args, **kwargs):
        resp = super().request(method, url, *args, **kwargs)
        resp.raise_for_status()
        return resp


class ZohoCrmClient(BaseZohoCrmClient):
    def upsert_contact(self, payload, duplicate_check_fields=None):
        params = {
            "duplicate_check_fields": duplicate_check_fields
        }
        return self.post(self._build_url("/Contacts/upsert"), params=params, json=payload).json()

    def update_contact(self, payload):
        return self.put(self._build_url("/Contacts"), json=payload).json()

    def create_contact(self, payload):
        return self.post(self._build_url("/Contacts"), json=payload).json()

    def delete_contact(self, ids):
        if len(ids) > 100:
            raise ValueError("Maximum 100 ids can be deleted at one time")
        return self.delete(
            self._build_url("/Contacts"),
            params={"ids": ','.join(map(str, ids))}
        ).json()
