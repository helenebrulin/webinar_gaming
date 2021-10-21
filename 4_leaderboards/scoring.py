#!/usr/bin/env python

import csv
import sys
import redis
import random


client = redis.Redis(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000)

list = ['vassilis', 'rahul', 'thomas', 'quinton', 'theodor', 'guy', 'rakhilaa', 'bill', 'ben', 'bob']


value = True
while (value):
    player = random.choice(list)
    score = random.randint(1,1000)
    client.zincrby("ldboard", score, player)
    print(player, ": +", score)