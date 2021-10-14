#!/usr/bin/env python

import random
import time
from redistimeseries.client import Client

rts = Client(host="redis-12000.internal.helene-eu-cluster.demo.redislabs.com", port=12000)

NOW=int(time.time()/86400)*86400
DAYS=365

for i in reversed(range(DAYS)):

    ts = 1000*(NOW-(86400*i))

    ###############################################################################################
    # Set some ARPU numbers
    arpu = 1 + random.randint(1, 10) + min((random.random() + .6), 1.2) * ((365 - i) * .25)
    rts.add("ARPU", ts, arpu)
    rts.redis.set("ARPU_TODAY", arpu)


    ###############################################################################################
    # Set some Daily Active Users
    dau = 1000000 + (365-i)*8220
    rts.add("DAU", ts, dau)
    rts.redis.set("DAU_TODAY", dau)

    ###############################################################################################
    # Build some load times
    if i > 90:
        login_time = 10 + 3 * random.random()
        daily_purchases = dau * (arpu/30) * .2
    else:
        login_time = 2 + random.random()
        daily_purchases = dau * (arpu/30) * .45

    app_time = 21 + 2 * random.random()
    rts.add("LOAD_LOGIN", ts, login_time)
    rts.redis.set("LOGIN_TODAY", login_time)

    rts.add("LOAD_APP", ts, app_time)
    rts.redis.set("APP_TODAY", app_time)

    rts.add("DAILY_PURCHASES", ts, daily_purchases)
    rts.redis.set("REVENUE_TODAY", daily_purchases)