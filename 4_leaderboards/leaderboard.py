#!/usr/bin/env python

import csv
import sys
import redis
import threading

client = redis.StrictRedis(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000, charset="utf-8", decode_responses=True)


def get_top():
    threading.Timer(1.0, get_top).start()
    print('\n')
    top = client.zrevrange("ldboard", 0, 4, withscores=True)
    for idx, player in enumerate(top):
        print(idx + 1, ' - ', player)


get_top()