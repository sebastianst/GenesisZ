# Copyright (C) 2016-2017 Sebastian Stammler
#
# This file is part of GenesisZ.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of GenesisZ, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

import requests

def _get_latest_BTC():
    data = _api_request_json('https://blockchain.info/latestblock')
    return data['height'], data['hash']

def _get_latest_ETH():
    data = _api_request_json('https://etherchain.org/api/blocks/count')
    number = data['data'][0]['count']
    data = _api_request_json('https://etherchain.org/api/block/%i' % number)
    _hash = data['data'][0]['hash']
    return number, _hash

def _get_latest_ZEC():
    data = _api_request_json('https://api.zcha.in/v2/mainnet/network')
    return data['blockNumber'], data['blockHash']

def _api_request_json(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('API call %s returned status code %i' %\
                url, r.status_code)
    return r.json()

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
