import requests
import re
import datetime

class APIClient(object):

    def __init__(self, config):

        # OAuth access token cache
        self._access_token = None
        self._access_token_expiry = None

        self.config = config

        # requests lib 'verify' param is either boolean or a custom CA cert path so has 3 states:
        # true = verify with default CA certs
        # false = don't verify
        # path = verify with custom CA cert
        if config.tls_verify and config.tls_ca_cert:
            self.tls_verify = config.tls_ca_cert
        else:
            self.tls_verify = config.tls_verify

    def _request(self, method, url, body=None, params={}, headers={}):

        headers['Authorization'] = "Bearer "+self.access_token()

        print(method, url, params)

        if body:
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'

            # application/json, application/geo+json etc
            if re.search('json', headers['Content-Type'], re.IGNORECASE):
                return requests.request(method=method,
                                        url=url,
                                        json=body,
                                        headers=headers,
                                        params=params,
                                        timeout=self.config.timeout,
                                        verify=self.tls_verify)
            
            else:
                return requests.request(method=method,
                                        url=url,
                                        data=body,
                                        headers=headers,
                                        params=params,
                                        timeout=self.config.timeout,
                                        verify=self.tls_verify)
        else:
            return requests.request(method=method,
                                    url=url,
                                    headers=headers,
                                    params=params,
                                    timeout=self.config.timeout,
                                    verify=self.tls_verify)

                

    def field_search(self, payload={}, limit=5, offset=None):
        url = self.config.base_url
        if not url.endswith("/"):
            url += "/"
        url += "field-searches"

        querystring = {"limit":limit}

        headers = {
            "Content-Type": "application/geo+json",
        }

        response = self._request(method="POST", url=url, body=payload, headers=headers, params=querystring)

        return response

    def get_boundaries(self, args={}, limit=5, offset=None):
        url = self.config.base_url
        if not url.endswith("/"):
            url += "/"
        url += "boundaries"

        args['limit'] = limit
        if offset:
            args['offset'] = offset

        headers = {
            "Accept": "application/geo+json",
        }

        response = self._request(method="GET", url=url, body=None, headers=headers, params=args)

        return response

    def access_token(self):
        
        # Refresh token if necessary
        if self._access_token and self._access_token_expiry >= datetime.datetime.now():
            return self._access_token

        # Refresh token 
        payload = "grant_type=client_credentials&client_id={}&client_secret={}&audience={}".format(self.config.client_id, self.config.client_secret, "https://api.varda.ag/fid/")

        headers = { 'Content-Type': "application/x-www-form-urlencoded" }

        print("Fetching token from "+self.config.token_url+" using client ID "+self.config.client_id)
        start = datetime.datetime.now()
        res = requests.post(self.config.token_url, data=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

        if 'access_token' not in data or 'expires_in' not in data:
            raise APIException(status=401, reason="Malformed token response")

        try:
            expires_seconds = int(data['expires_in'])
        except ValueError:
            raise APIException(status=401, reason="Malformed token response")

        self._access_token = data['access_token']
        self._access_token_expiry = start + datetime.timedelta(seconds=expires_seconds - self.config.token_expiry_buffer)

        return self._access_token

class APIConfiguration(object):

    def __init__(self):
        # Default Base url
        self.base_url = "https://api.varda.ag/fid/v1/"

        # OAuth credentials
        self.client_id = ""
        self.client_secret = ""

        # Auth config
        self.token_url="https://auth.varda.ag/oauth/token"
        # Buffer (in seconds) used to refresh token before it expires
        self.token_expiry_buffer = 10

        # Client-side request timeout
        self.timeout = 10

        # Set to false to skip TLS cert verification.
        self.tls_verify = True
        # Set to customize the CA certificate for server certificate verification.
        self.tls_ca_cert = None

class APIException(Exception):

    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """Custom error messages for exception"""
        error_message = "({0})\n"\
                        "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(
                self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message
