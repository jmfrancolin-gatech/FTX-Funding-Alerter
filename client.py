import time
import hmac
from requests import Request, Session, Response

class FtxClient:
    ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None):
        self.session = Session()
        self.api_key = api_key
        self.api_secret = api_secret

    def get(self, path: str, params=None):
        return self.request('GET', path, params=params)

    def request(self, method: str, path: str, **kwargs):
        request = Request(method, self.ENDPOINT + path, **kwargs)
        self.sign_request(request)
        response = self.session.send(request.prepare())
        return self.process_response(response)

    def sign_request(self, request: Request):
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self.api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self.api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)

    def process_response(self, response: Response):
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']