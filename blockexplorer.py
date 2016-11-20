import requests

def _get_latest_BTC():
    r = _api_request('https://blockchain.info/latestblock')
    data = r.json()
    return data['height'], data['hash']

def _get_latest_ETH():
    r = _api_request('https://etherchain.org/api/blocks/count')
    number = r.json()['data'][0]['count']
    r = _api_request('https://etherchain.org/api/block/%i' % number)
    _hash = r.json()['data'][0]['hash']
    return number, _hash

def _get_latest_ZEC():
    r = _api_request('https://api.zcha.in/v1/mainnet/network')
    data = r.json()
    return data['blockNumber'], data['blockHash']

def _api_request(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('API call %s returned status code %i' %\
                url, r.status_code)
    return r

_getter = \
        {'BTC': _get_latest_BTC,
         'ETH': _get_latest_ETH,
         'ZEC': _get_latest_ZEC}

def get_latest(coin='BTC'):
    """returns the latest block number and hash for the given coin.
    Currently supported coins: BTC, ETH, ZEC"""
    if coin not in _getter:
        raise UnsupportedCoin('Coin %s not supported.')
    number, _hash = _getter[coin]()
    if _hash.startswith('0x'):
        _hash = _hash[2:]
    return number, _hash

def UnsupportedCoin(BaseException):
    pass
