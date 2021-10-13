#!/usr/bin/env python

import csv

from redisearch import Client, IndexDefinition, TextField, GeoField

client = Client(
    'cities-v1',
    host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com",
    port=12000
    )

pipe = client.redis.pipeline(transaction=False)

definition = IndexDefinition(
    prefix=['city:'],
    language='English',
)


client.create_index(
    (
        GeoField("location"),
        TextField('city'),
        TextField('city_display'),
        ),
    definition=definition
    )


with open('worldcities.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    row_count = 0
    for row in reader:
        if row['population'] != '':
            if float(row['population']) >= 1200000:
                pipe.hset("city:%s" %(row['city_ascii'].replace(" ", "_")),
                    mapping = {
                        "city": row['city_ascii'].replace(" ", "_"),
                        "city_display": row['city_ascii'],
                        "location": "{},{}".format(row['lng'], row['lat'])
                        }
                )
                row_count += 1
                if row_count % 500 == 0:
                    pipe.execute()

pipe.execute()
client.aliasadd("cities")
