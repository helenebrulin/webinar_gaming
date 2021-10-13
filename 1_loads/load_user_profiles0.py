#!/usr/bin/env python

import csv
import sys
import redis

client = redis.Redis(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000)

pipe = client.pipeline(transaction=False)

if len(sys.argv) > 1:
    load_file = sys.argv[1]
else:
    load_file = 'pop_users.csv'

with open(load_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    row_count = 0
    for row in reader:
        pipe.hset("user:%s" %(row['username']), mapping = row)
        row_count += 1
        if row_count % 500 == 0:
            pipe.execute()

pipe.execute()
