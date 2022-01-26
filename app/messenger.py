"""
Desc:
messenger.py parses Binance <symbol>@bookTicker data stream, then stores
formatted data in Redis. Defaults to btcusdt@bookTicker.
Usage:
python messenger.py [symbol]
Example:
python messenger.py
python messenger.py bnbbtc
python messenger.py btcusdt bnbbtc ... bnbbusd
Note:
Stable up to 2 streams, further performance enhancement needed.
"""
import sys
import time
import redis
from binance import ThreadedWebsocketManager  # no need to reinvent the wheel
from console import console
from module import db
import cfg

DEBUG = cfg.DEBUG
RDB_HOST = cfg.RDB_HOST
RDB_PORT = cfg.RDB_PORT

rdb = redis.Redis(host=RDB_HOST, port=RDB_PORT)

def handle_bookticker_socket_msg(msg: dict) -> None:
    """
    "s":"BNBUSDT",      // symbol
    "b": "0.0024",      // Best bid price // bid_price
    "B": "10",          // Best bid quantity // bid_quantity
    "a": "0.0026",      // Best ask price // ask_price
    "A": "100",         // Best ask quantity // ask_quantity
    READ: https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#subscribe-to-a-stream
    """
    # parse msg
    try:
        ts = time.time()
        symbol = msg['data']['s']
        bid_price = msg['data']['b']
        bid_quantity = msg['data']['B']
        ask_price = msg['data']['a']
        ask_quantity = msg['data']['A']
    except Exception as e:
        # possible failure point in case malformed msg, await furthur handling.
        console.log(e)
        return

    # prep redis payload
    rdb_key = f'transmute:bookticker:{symbol.lower()}'
    rdb_payload = {
        'ts': str(ts),
        'symbol': symbol,
        'bid_price': str(bid_price),
        'bid_quantity': str(bid_quantity),
        'ask_price': str(ask_price),
        'ask_quantity': str(ask_quantity),
    }

    if DEBUG:
        console.log(f'{ts=}, {bid_price=}, {bid_quantity=}, {ask_price=}, {ask_quantity=}')
        console.log(f'{rdb_key=}')
        console.log(f'{rdb_payload=}')

    db.set_redis_json(rdb=rdb, key=rdb_key, path='.', payload=rdb_payload)
    db.set_redis_expire(rdb=rdb, key=rdb_key, seconds=1)


def main(argv):
    l_symbols = ['btcusdt']
    if len(sys.argv) > 1:
        l_symbols = sys.argv[1:]
    l_streams = [f'{symbol}@bookTicker' for symbol in l_symbols]

    if DEBUG:
        console.log(l_streams)

    # this reconnects automatically during connection loss.
    twm = ThreadedWebsocketManager()
    twm.start()
    twm.start_multiplex_socket(
        callback=handle_bookticker_socket_msg,
        streams=l_streams,
    )
    twm.join()

if __name__ == '__main__':
   main(sys.argv)
