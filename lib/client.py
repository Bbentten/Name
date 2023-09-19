import logging
import json
import json_minify
import time
import urllib.parse
import requests
import yarl

from . import utils, objects, defaults

log = logging.getLogger('urllib3')
log.setLevel(logging.WARNING)

__all__ = ('Client',)


def getfullurl(url, params=None, cid=None, globalndc=False, ssl=False):
    """prepare api full url with only path url."""
    base =  ('https' if ssl else 'http') + '://service.narvii.com/api/v1/'
    ndc = f'g-x{cid}/s/' if cid and globalndc else f'x{cid}/s/' if cid else 'g/s/'
    url = urllib.parse.urljoin(ndc, url.removeprefix('/'))
    url = urllib.parse.urljoin(base, url)
    if isinstance(params, dict):
        url += '?%s' % urllib.parse.urlencode(params, encoding='utf-8')
    return url

class Client:

    api = yarl.URL('http://service.narvii.com/api/vi')

    def __init__(self, device=None, proxy=None) -> None:
        self.device = utils.update_device(device) if device else utils.device_gen()
        self.proxy = proxy
        self.http = requests.Session()
        self.accept_encoding = defaults.accept_encoding
        self.accept_language = defaults.accept_language
        self.connection = defaults.connection
        self.user_agent = defaults.user_agent
        self.sid, self.auid, self.ndcId = None, None, None
        self.played_lottery = 0.0
        self.user, self.account = objects.UserProfile({}), objects.Account({})

    def prepare_headers(self, data=None, *, minify=False, type=None):
        headers = {
            'Accept-Encoding': self.accept_encoding,
            'Accept-Language': self.accept_language,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'NDCDEVICEID': self.device,
            'HOST': self.api.host,
            'User-Agent': self.user_agent,
            'Connection': self.connection
        }
        if self.sid is not None:
            headers['NDCAUTH'] = 'sid=%s' % self.sid
        if type and isinstance(type, str):
            headers['Content-Type'] = type
        if isinstance(data, dict):
            if 'timestamp' not in data:
                data['timestamp'] = int(time.time() * 1000)
            data = json.dumps(data)
            if minify:
                data = json_minify.json_minify(data)
            headers['NDC-MSG-SIG'] = utils.signature_gen(data)
            headers['Content-Lenght'] = str(len(data))

        return headers

    def request(self, method, url, params=None, data=None, *, cid=None, globalndc=False, minify=False):
        url = getfullurl(url, cid=cid, globalndc=globalndc)
        log.info('New Request - %r - %r', method, url)
        headers = self.prepare_headers(data, minify=minify)
        if isinstance(params, dict):
            if 'timezone' not in params:
                params['timezone'] = 0
        if isinstance(data, dict):
            if 'timestamp' not in data:
                data['timestamp'] = int(time.time() * 1000)
            data = json.dumps(data)
            if minify:
                data = json_minify.json_minify(data)
        response  = self.http.request(method,url, params=params, data=data, headers=headers)
        if response.status_code != 200:
            log.error('%r request - status=%d' % (url, response.status_code))
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = dict()
        return data

    def get_from_link(self, link):
        return self.request('GET', 'link-resolution', params=dict(q=link))

    def login(self, email, password):
        data = self.request('POST', 'auth/login', data=dict(v=2, email=email, action='normal', secret=f'0 {password}', deviceID=self.device, clientType=100))
        if data.get("api:statuscode") == 0:
            self.auid, self.sid = data['auid'], data['sid']
            self.account.json.clear(); self.user.json.clear()
            self.account.json.update(data['account'])
            self.user.json.update(data['userProfile'])
        return data

    def login_sid(self, sid):
        self.auid, self.sid = self.device, sid

    def join_community(self, ndcId, invitationId):
        data = dict(invitationId=invitationId) if invitationId else {}
        data = self.request('POST', 'community/join', cid=ndcId, data=data)
        if data.get('api:statuscode') == 0:
            self.ndcId = ndcId
        return data

    def play_lottery(self, ndcId, tz=0):
        resp = self.request('POST', 'check-in/lottery', cid=ndcId, data=dict(timezone=tz))
        if resp.get('api:statuscode') == 0:
            self.played_lottery = time.time()
        return resp

    def send_activity(self, ndcId, activity, tz=0):
        return self.request('POST', 'community/stats/user-active-time', cid=ndcId, data=dict(timezone=tz, optInAdsFlags=2147483647, userActiveTimeChunkList=activity), minify=True)
