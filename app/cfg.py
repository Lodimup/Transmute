"""
Desc:
Config file for Transmute.
"""
import os

DEBUG = True
RDB_HOST = 'localhost'
RDB_PORT = 6379

if os.environ.get('RDB_HOST'):
    RDB_HOST = os.environ.get('RDB_HOST')
