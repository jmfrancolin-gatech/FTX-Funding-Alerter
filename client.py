import time
import hmac
from requests import Request, Session, Response

class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None):
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret

    def get(self, ts: int, path: str, params=None):
        return self._request(ts, 'GET', path, params=params)

    def _request(self, ts: int, method: str, path: str, **kwargs):
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(ts, request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, ts: int, request: Request):
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)

    def _process_response(self, response: Response):
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']