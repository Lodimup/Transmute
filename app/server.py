"""
Desc:
server.py serves data from redis.
Usage:
python server.py
Note:
Possibility to dynamically generate endpoints in furture updates.
"""
import redis
from flask import (
    Flask,
    request,
)
import cfg
from module import db

DEBUG = cfg.DEBUG
RDB_HOST = cfg.RDB_HOST
RDB_PORT = cfg.RDB_PORT

app = Flask(__name__)
rdb = redis.Redis(host=RDB_HOST, port=RDB_PORT)

@app.route("/snapshot/BTC_USDT", methods=['GET', 'POST', 'DELETE', 'PATCH'])
def BTC_USDT():
    key = 'transmute:bookticker:btcusdt'

    if request.method == 'POST':
        payload = db.get_redis_json(rdb, key)

        # handle stale payload
        if not payload:
            dct_err = {
                'status_code': 500,
                'error': f'{key} stale.',
                }
            return dct_err, 500

        payload.pop('symbol', None)
        return payload, 200

    # handle unsupported request catchall
    dct_err = {
        'status_code': 400,
        'error': f'{request.method} not supported.',
        }
    return dct_err, 400

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=4444)
