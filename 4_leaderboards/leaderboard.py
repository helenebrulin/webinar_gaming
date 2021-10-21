#!/usr/bin/env python

import csv
import sys
import redis
import threading

client = redis.Redis(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000)


def get_top():
    threading.Timer(1.0, get_top).start()
    print('\n')
    top = client.zrevrange("ldboard", 0, 4)
    for idx, player in top:
        print(idx + 1, ' - ', player, '\n')


    print(top)


get_top()