#!/usr/bin/env python

import csv
import sys
import redis
import random


client = redis.Redis(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000)

list = ['vassilis', 'rahul', 'thomas', 'quinton', 'theodor', 'guy', 'rakhilaa', 'bill', 'ben', 'bob']

#load_file = 'scores.csv'

#with open(load_file, newline='') as csvfile:
#    reader = csv.DictReader(csvfile)
#    row_count = 0
#    for row in reader:
#        client.zincrby("ldboard", row['score'], row['player'])
#        print(row['player'], ": +", row['score'])
#        row_count += 1



value = True
while (value):
    player = random.choice(list)
    score = random.randint(1,1000)
    client.zincrby("ldboard", score, player)
    print(player, ": +", score)