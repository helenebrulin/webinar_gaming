#!/usr/bin/env python

import csv
import redis
from redisearch import Client, IndexDefinition, TextField, NumericField, TagField 


client = Client(
        'MatchMaker-idx',
        host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com",
        port=12000)

definition = IndexDefinition(
           prefix=['ticket:'],
           language='English',
           score_field='title',
           score=0.5
           )

client.create_index(
        (
            TextField("username", weight=5.0),
            NumericField('mmr', sortable=True),
            NumericField('experience', sortable=True),
            TagField('group_tags'),
            TagField('secondary_group_tags'),
            TagField('blacklist_tags'),
            TagField('play_style_tags'),
            NumericField('rating', sortable=True),
            TextField("pop", weight=5.0)
            ),
        definition=definition)

pipe = client.redis.pipeline(transaction=False)

with open('sample_users.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    row_count = 0
    for row in reader:
        pipe.hset("ticket:%s" %(row['username']), mapping = row)
        row_count += 1
        if row_count % 500 == 0:
            pipe.execute()

pipe.execute()
