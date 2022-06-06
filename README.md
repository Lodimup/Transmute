# Transmute
Transmute is a POC of a micro service which translates Binance websocket market data to REST API. Data is “transmuted” and stored in redis, then served using flask. The whole service can simply be brought up with

```python
docker compose up
```
# Objective

POC a service that lets user fetch crypto data from Binance websocket stream <symbol>@bookTicker in a sane way using flask.

# Constrains

websocket must remain open

# Extended goal!

-   Supports all symbols on data stream side
-   Never serve stale data
-   Docker compose

# What's next?
- Dynamic routing, on any valid symbol
- Additional stream types
- Auto spawn socket process based on request
- Auto de-spawn socket when not used
- Upgrade to Django
# Usage

```python
git clone <https://github.com/Lodimup/Transmute.git>
cd Transmute
docker compose build --no-cache && docker compose up -d
// if you want to see what's going on inside remove -d flag like so:
docker compose build && docker compose up

```

Then

open  [](http://localhost:3333/)[http://localhost:3333](http://localhost:3333/)  in your favorite browser

POST  [](http://127.0.0.1:3333/snapshot/BTC_USDT)[http://127.0.0.1:3333/snapshot/BTC_USDT](http://127.0.0.1:3333/snapshot/BTC_USDT)  using Postman
NOTICE: It SHOULD bet GET here, but the person given this challenge explicitly requested POST to be swapped with GET.
  
Try GET  [](http://127.0.0.1:3333/snapshot/BTC_USDT)[http://127.0.0.1:3333/snapshot/BTC_USDT](http://127.0.0.1:3333/snapshot/BTC_USDT)  it will return an error 400

Try shutting down messenger, let TTL runs out, then

Try POST  [](http://127.0.0.1:3333/snapshot/BTC_USDT)[http://127.0.0.1:3333/snapshot/BTC_USDT](http://127.0.0.1:3333/snapshot/BTC_USDT)  it will return an error 500, stale data

You can see what’s going on inside redis db using redis-cli and redis-insight

redis-insight

See what’s going on inside the db

[](https://redis.com/redis-enterprise/redis-insight/)[https://redis.com/redis-enterprise/redis-insight/](https://redis.com/redis-enterprise/redis-insight/)  choose the 2.x version

redis-cli

See what’s goin on inside the db using CLI

```python
cd ~/
mkdir tmp
cd tmp
curl <http://download.redis.io/redis-stable.tar.gz> -o redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
make test //optional
sudo cp src/redis-server /usr/local/bin/
sudo cp src/redis-cli /usr/local/bin/
redis-cli monitor

```

# Dev Notes

There are two main options

1.  **Use multiprocessor**

Since we need socket to remain open and it is not thread safe. We must use multiprocessor. to spawn two processes, flask, and web socket. Data is shared through an object. Although, this requires no database it’s very complicated to the point of over engineering. If served using gunicorn websocket will possibly be spawned for each request which is never good. Extending functionality is hard too since the two processes are tied together via data object.

1.  **Run messenger, and server separately as micro-services with Redis**

Redis is very easy to spin up using docker. It’s no brainer to use it as a data store.  messenger.py connects to Binance via websocket, translates data, then stores in Redis.  server.py  fetches the data from Redis then serves the API. Redis has nice added benefit, we can set TTL so  **we can never serve stale data**. We can also spawn multiple  messenger.py easily if required. Although not required, persistence can be easily enabled with -v flag

**We select option 2**

## messenger.py

Desc:  messenger.py  parses Binance <symbol>@bookTicker data stream, then stores formatted data in Redis. Defaults to btcusdt@bookTicker. Usage:

```python
python messenger.py
```

Example:

```python
python messenger.py
python messenger.py bnbbtc
python messenger.py btcusdt bnbbtc ... bnbbusd

```

## server.py

Desc:  server  serves data from redis. Usage:

```python
python server.py
```

Note: Possibility to dynamically generate endpoints in furture updates.

Note: Stable up to 2-4 streams depending on Binance’s mood, further performance enhancement needed. Since it’s POC, case where Binance dies is not handled. Easiest workaround is just sending a signal to restart the docker compose.

Add credentials to database connection if used in a production environment
