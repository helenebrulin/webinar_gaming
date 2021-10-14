# Setup

## Start instances

- Start machines, create db with search and timeseries. Only one shard.
- Git clone this in fourth machine.

## Setup venv on each terminal

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Send pop_users file to gcloud instance
gcloud compute scp pop_users.csv --zone "europe-west1-b" "helene-gaming":~
sudo mv pop_users.csv /root

## Install go
```sh
wget https://dl.google.com/go/go1.16.4.linux-amd64.tar.gz 
sudo tar -xvf go1.16.4.linux-amd64.tar.gz   
sudo mv go /usr/local 

#for all sessions
export GOROOT=/usr/local/go 
export GOPATH=/root
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH 
```

-------

## Install Configure Grafana
https://www.linuxfordevices.com/tutorials/ubuntu/install-grafana-on-ubuntu-debian
grafana-cli redis plugin
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
open tcp port 3000 in vpc as well as in doc above

install terraform : https://www.decodingdevops.com/how-to-install-terraform-on-ubuntu-18-04-server/ 
https://www.terraform.io/downloads.html

```sh
cd terraform
terraform init
terraform apply
```
- Open the two dashboards in IP 3000

## Configure RedisInsight
- use helene-eu-cluster.demo.redislabs.com + port 9443!!


----------

## Load data

```sh
cd loads
./load_cities.py
./load_user_profiles0.py ../pop_users.csv # for grafana part
go run stats.go #metrics engine listening to matches
go run loader.go -f ../pop_users.csv #sends tickets to matchmaking engine.
```

## Load fake KPIs (do not do it during demo)
pip install redistimeseries # add this to requirements
./gen_game_metrics.py

# SETUP DONE

--------

# Show Grafana KPI board (NO)
- Open KPIs board
- We have 4 million users, populated over a year. This is a Grafan integration with Redis Time Series. 
- We see revenue per users here
- And monthly active users bucketed by month. 
- Current nb of active users and current avg revenue per user.
- We have load times, which is critical. 10s and we see a drop when we switched over to redis. 
- zoom in and get closer look

# Show matchmaking

- We will start matchmaking now in real time

```sh
cd matchmaking &&  go run matchmaker.go
```

- Left : Matching in real time. We have our leaderboards. Lead by PoP, you can see that most people are closest to Auckland. You see that real time  as matches occur. 

- Middle : We have our group leaders so you can see which people in which groups are matching the quickest.

- Right : And we’re modifying the scores of the players in real time.

And at the bottom : matches in real time. We're matcting around 15 a second - BAD PERFORMANCE ???
And right is total nb of matches. 


# PART 2

## Streams
- open redis Insight click on Streams. (CLICK ON SCAN BELOW TO GET SOME KEYS)
- This is our backfill, our queue sent to pop servers.
- As users are coming and we’re matching them out so different streams. 
Those are the messages that come in. 
So on our ?? server or point of presence, we have this request coming, with the user names. These are updating in real time as we’re doing the backfill as that last step in matching process.


# PART 3

- Now let's stop the matching algorithm and look at how you implement one in detail.

```sh
./load_user_profiles.py # for search part 
```

- This is using redisInsight, web UI which allows you to view redis in real time, with features like memory analysis and profiler.
So here in redis CLI we’re going to do a simple match query with redisSearch : 

```sh
FT.SEARCH MatchMaker-idx "*" LIMIT 0 4 RETURN 3 username mmr pop
```

- FT.SEARCH is a redis search module command to search. MatchMaker-v1 is the name of out index. 
We limit the search to 4 results and we're just going to return these 3 fields per result. 

- we're going to search through everything and return a 4 user names, mmrs and pops.
See that we've got Pamela, Connor, ... and James.
MMRs are pretty diverse, so they are all over the board.
The PoPs as well. Terrible for network latencies. So limit those to a single point of presence : Tokyo. 

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo" LIMIT 0 4 RETURN 3 username mmr pop
```
MMRs are still disparate. 
SO we narrow it down again. 

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872]" LIMIT 0 4 RETURN 3 username mmr pop
```

Search numerically between those mmr. 
Now we've returned users with closer mmr, for a better game experience.

- What about removing blacklisted users? 
```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872] -@user:(loganderek|mybrother)" LIMIT 0 4 RETURN 3 username mmr group_tags
```
Here we also want to return the group tags as well when displaying our results, so we add that.

- We see that we have two reslults in darkgrey-posse, so maybe we want to add an optional search for this group, so that users in that group would rank first in this matchmaking process.

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872] -@user:(loganderek|mybrother) ~@group_tags:{darkgray_posse}" LIMIT 0 4 RETURN 3 username mmr group_tags
```

- now we see one of the players that was there before but was not in darkgray-posse is not here anymore, and our first top three results are in that group. So all of the members in that group are here now.

- Let's add another optional search based on the secondary group tag 

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872] -@user:(loganderek|mybrother) ~@group_tags:{darkgray_posse} ~@secondary_group_tags:{thistle_pack}" LIMIT 0 4 RETURN 4 username mmr group_tags secondary_group_tags
```

- You can play with individual weights dynamically as well for those optional searcges

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872] -@user:(loganderek|mybrother) ~@group_tags:{darkgray_posse} => { $weight: 30.0} ~@secondary_group_tags:{darkgoldenrod_squad} => {$weight: 100.0}" LIMIT 0 4 WITHSCORES RETURN 4 username  group_tags secondary_group_tags play_style_tags
```

- Here we can weight the first group tag lower than the secondary one, and put the secondary one as darkgoldenrod_squad. And we see that the top result is now not in darkgray_posse since secondary group tag is weighted more than the primary group tag. 
- WITHSCORES will give us the score also for all the results
  

- We can also run this EXPLAINSCORE command with our matching : 

```sh
FT.SEARCH MatchMaker-idx "@pop:Tokyo @mmr:[2731 2872] -@user:(loganderek|mybrother) ~@group_tags:{darkgray_posse} => { $weight: 30.0} ~@secondary_group_tags:{darkgoldenrod_squad} => {$weight: 100.0}" LIMIT 0 1 WITHSCORES EXPLAINSCORE RETURN 1 username 
```

- So here i'm just showing the top results with only the username, and i'm showing the output of EXPLAINSCORE.
- So we see the method of scoring TFIDF : RediSearch allows you to use different scoring algorithms

TFIDF : term frequency–inverse document frequency, it is a numerical statistic that is intended to reflect how important a word is to a document in a collection or corpus


- And finally, let's do a geo search to find the closest PoP
```sh
 FT.AGGREGATE cities '*' LOAD 2 location city APPLY "geodistance(@location, -122.4475743, 37.7722695)" as dist SORTBY 2 @dist ASC LIMIT 0 1
 ```
  -> Aggregate the cities.
  -> We are going two load two things : the location field and the city name. And apply our geodistance location function here and sort this by distance. by default this distance is in meters. 

