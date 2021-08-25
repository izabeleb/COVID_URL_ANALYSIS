import requests
import tweepy
import time
import csv
from datetime import datetime
from os import path

class TweetProcessor:
    
    def __init__(self, tweepy_consumer_key, tweepy_consumer_secret, tweepy_filter,
                 vt_keys, batch_size):
        
        self.tweepy_consumer_key = tweepy_consumer_key
        self.tweepy_consumer_secret = tweepy_consumer_secret
        self.tweepy_filter = tweepy_filter
        
        self.vt_keys = vt_keys
        self.vt_key_limit_status = ["nolimit" for i in range(len(self.vt_keys))]
        self.vt_key_limit_minute_start = [0 for i in range(len(self.vt_keys))]
        
        # batch size is between 1-500
        self.batch_size = batch_size
        self.total_tweets_to_retrieve = self.batch_size * len(vt_keys)
        
        self.tweet_id_set = self.construct_tweet_id_set()
        self.tweet_dict = {}
        self.queued_scans = []
        self.keys_maxed_out = False
        
        self.positives_dict = dict()
        
        self.headers = ['tweet_id','url','text','created_at','source','retweet_count',
                        'favorite_count','id_str','name','screen_name','location',
                        'description','verified','followers_count','friends_count',
                        'listed_count','favourites_count','statuses_count',
                        'user_created_at','lang','contributers_enabled','is_translator',
                        'user_background_color','queued','positives','total']
        
        
        self.outputfile = 'csvfile.csv'
        
        if path.exists(self.outputfile):
            self.csvfile = open(self.outputfile,'a+', encoding="utf-8", newline='')
            self.writer = csv.writer(self.csvfile)
        else:
            self.csvfile = open(self.outputfile,'a+', encoding="utf-8", newline='')
            self.writer = csv.writer(self.csvfile)
            self.writer.writerow(self.headers)
        
        self.processed_tweets = 0
        
    def get_tweet_dict(self):
        return self.tweet_dict
    
    def get_tweet_id_set(self):
        return self.tweet_id_set
    
    def write_tweet_data(self, tweet_id, tweet_dict):    
    
        line = [tweet_id]
                
        for value in tweet_dict.values():
                    
            line.append(value)
                
        self.writer.writerow(line)   
        
        self.processed_tweets += 1
    
    def close_file(self):
        self.csvfile.close()
    
    def run(self):
        print("starting tweet retrieval")
        self.retrieve_tweets()
        print("retrieved tweets, starting vt processing")
        print("----------------------------------------")
        
        self.vt_analysis()
        print("analysis complete, starting retrieval of queued scans")
        print("----------------------------------------")
        
        print("waiting before retrieving queued scans")
        # waiting before retrieving queued scans
        time.sleep(100)
        
        self.retrieve_queued_scans()
        print("number of tweets retrieved and processed: " + str(len(self.tweet_dict)))
        print("sucessfully completed tweet retrieval and virus total analysis")
        print(datetime.now())
        self.close_file()
        
        positives_string = ""
        
        for k,v in self.positives_dict.items():
            positives_string += str(k) + ":" + str(v) + " , "
            
        print("Positives results: [" + positives_string + "]")
        
        with open("tweetProcessorLog.txt", "a") as file:
            file.write("\n" + str(datetime.now()) + ", num tweets processed: " + str(len(self.tweet_dict)) + ", filter used: " + self.tweepy_filter
                        + ", Positives results: [" + positives_string + "]")
    
    def retrieve_queued_scans(self):
        
        current_key_index = 0
        current_tweet = 0
        
        while current_tweet < len(self.queued_scans):
        
        #for tweet_id, scan_id in self.queued_scans:
        
            tweet_id = self.queued_scans[current_tweet][0]
            scan_id = self.queued_scans[current_tweet][1]
    
            if self.keys_maxed_out:
                print("keys maxed out")
                break
            
            self.vt_key_limit_minute_start[current_key_index] = time.time()
            vt_call_results = self.vt_api_call(self.vt_keys[current_key_index],
                                               scan_id)
            
            print(str(vt_call_results) + " response for key in index " + str(current_key_index))
            
            if vt_call_results[0] == 200: # data sucessfully retrieved
                
                current_tweet += 1
                self.vt_key_limit_status[current_key_index] = "nolimit"
                if vt_call_results[1] == "queued":                    
                    self.tweet_dict[tweet_id]["2nd try no result"] = "true"
                    print("URL not retrieved, 2nd try no result")
                else:
                    self.tweet_dict[tweet_id]["vt_positives"] = vt_call_results[2]
                    self.tweet_dict[tweet_id]["vt_total"] = vt_call_results[3]
                    #print("URL data retrieved for " + str(self.tweet_dict[tweet_id]["url"]))
                    self.write_tweet_data(tweet_id, self.tweet_dict[tweet_id])
                    
                    if vt_call_results[2] not in self.positives_dict:
                        self.positives_dict[vt_call_results[2]] = 1
                    else:
                        self.positives_dict[vt_call_results[2]] += 1
            
            elif vt_call_results[0] == 204: # minute or daily limit reached
                
                # one of the key limits has been reached, set new status
                if self.vt_key_limit_status[current_key_index] == "nolimit":
                    self.vt_key_limit_status[current_key_index] = "minlimit"
                    print("key " + str(current_key_index) + " minlimit reached")
                elif self.vt_key_limit_status[current_key_index] == "minlimit":
                    self.vt_key_limit_status[current_key_index] = "dailylimit"
                    print("key " + str(current_key_index) + " dailylimit reached")
                # check that all keys haven't reached the daily limit
                endless_loop_counter = len(self.vt_keys)
                current_counter = 0
                while self.vt_key_limit_status[current_counter % len(self.vt_keys)] == "dailylimit":
                    if current_counter == endless_loop_counter:
                        print("all keys maxed out")
                        self.keys_maxed_out = True
                        return
                    else: 
                        current_counter += 1    
                    
                # if last key, wait minute between now and first key start time
                if current_key_index == len(self.vt_keys) - 1:
                    print("reached last key, waiting")
                    while time.time() - self.vt_key_limit_minute_start[0] < 61:
                        time.sleep(1)
                        
                # rotate key
                current_key_index = current_key_index + 1 % len(self.vt_keys)

        
    def vt_api_call(self, apikey, url):
        
        apiurl = 'https://www.virustotal.com/vtapi/v2/url/report?apikey={}&resource={}&scan=1'.format(apikey , url)
        r = requests.get(apiurl)
       
        request_status = r.status_code
        url_status = ""
        positives = 0
        total = 0
        scan_id = ""
        
        if request_status == 200 and str(r.json()["verbose_msg"]).startswith("Scan request successfully queued"):
            url_status = "queued"
            scan_id = str(r.json()["scan_id"])
        elif request_status == 200:
            #print(json.dumps(r.json()))
            try:
                
                positives = r.json()["positives"]
                total = r.json()["total"]
            except:
                print("ERROR: ", request_status, url_status, r.json())
            
            
        return [request_status, url_status, positives, total, scan_id]
    
    def retrieve_tweets(self):
        
        auth = tweepy.AppAuthHandler(self.tweepy_consumer_key, self.tweepy_consumer_secret)
        api = tweepy.API(auth)
        tweets = tweepy.Cursor(api.search, q=self.tweepy_filter).items(self.total_tweets_to_retrieve)         
        
        collected_tweets = 0
        for tweet in tweets:
            
            if tweet.id_str in self.tweet_id_set:
                print("duplicate tweet discovered, skipping")
                continue
            
            self.tweet_id_set.add(tweet.id_str)
            
            if collected_tweets > self.total_tweets_to_retrieve:
                break

            try:
                if "https://twitter.com/i/web/status/" not in tweet.entities["urls"][0]["expanded_url"]:
                    
                    collected_tweets += 1
                    print(tweet.entities["urls"][0]["expanded_url"])
                    self.tweet_dict[tweet.id_str] = dict([
                        ("url", tweet.entities["urls"][0]["expanded_url"]),
                        ("text", "\"" + str(tweet.text).replace('\n', ' ').replace('\r', ' ').replace('\r\n', ' ') + "\""),
                        ("created_at", tweet.created_at),
                        ("source", tweet.source),
                        ("retweet_count", tweet.retweet_count),
                        ("favorite_count", tweet.favorite_count),
                        ("user.id_str", tweet.user.id_str),
                        ("user.name", tweet.user.name),
                        ("user.screen_name", tweet.user.screen_name),
                        ("user.location", tweet.user.location),
                        ("user.description", tweet.user.description),
                        ("user.verified", tweet.user.verified),
                        ("user.followers_count", tweet.user.followers_count),
                        ("user.friends_count", tweet.user.friends_count),
                        ("user.listed_count", tweet.user.listed_count),
                        ("user.favourites_count", tweet.user.favourites_count),
                        ("user.statuses_count", tweet.user.statuses_count),
                        ("user.created_at", tweet.user.created_at),
                        ("user.lang", tweet.user.lang),
                        ("user.contributors_enabled", tweet.user.contributors_enabled),
                        ("user.is_translator", tweet.user.is_translator),
                        ("user.profile_background_color", tweet.user.profile_background_color)
                    ])
                else:
                    print("web status url discovered, skipping")
            except Exception as exc:
                print("error while collecting tweets: " + str(exc))
                
    def construct_tweet_id_set(self):
        
        tweet_id_set = set()
        # would return set of constructed tweet ids
        # either blank if it's a first run
        # or constructed from the tweet_id fields in the existing csv
            
        with open('csvfile.csv', encoding="utf-8", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tweet_id_set.add(row['tweet_id'])
        
        return tweet_id_set
    
    def vt_analysis(self):
    
        tweets_processed = 0
        current_key_index = 0
        current_tweet = 0
        
        keys = list(self.tweet_dict.keys())
        
        while current_tweet < len(self.tweet_dict) - 1:
            
            k = keys[current_tweet]
            
            if tweets_processed >= self.total_tweets_to_retrieve or self.keys_maxed_out:
                print("analyzed all tweets or keys are maxed out")                
                break
            
            self.vt_key_limit_minute_start[current_key_index] = time.time()
            vt_call_results = self.vt_api_call(self.vt_keys[current_key_index], self.tweet_dict[k]["url"])
            
            print(str(vt_call_results) + " response for key in index " + str(current_key_index))
            
            if vt_call_results[0] == 200:
                
                self.tweet_id_set.add(k)
                current_tweet += 1
                self.vt_key_limit_status[current_key_index] = "nolimit"
                if vt_call_results[1] == "queued":
                    tweets_processed += 2 # leaving enough of limit to retrieve this report later
                    self.queued_scans.append([k, vt_call_results[4]])
                    self.tweet_dict[k]["queued"] = "true"
                    #print("tweet URL analysis queued")
                else:
                    tweets_processed += 1
                    self.tweet_dict[k]["queued"] = "false"
                    self.tweet_dict[k]["vt_positives"] = vt_call_results[2]
                    self.tweet_dict[k]["vt_total"] = vt_call_results[3]
                    
                    if vt_call_results[2] not in self.positives_dict:
                        self.positives_dict[vt_call_results[2]] = 1
                    else:
                        self.positives_dict[vt_call_results[2]] += 1
                    
                    self.write_tweet_data(k, self.tweet_dict[k])
                    #print("tweet URL analysis returned")
            
            elif vt_call_results[0] == 204:   
                
                # one of the key limits has been reached, set new status
                if self.vt_key_limit_status[current_key_index] == "nolimit":
                    self.vt_key_limit_status[current_key_index] = "minlimit"
                    print("key " + str(current_key_index) + " minlimit reached")
                elif self.vt_key_limit_status[current_key_index] == "minlimit":
                    self.vt_key_limit_status[current_key_index] = "dailylimit"
                    print("key " + str(current_key_index) + " dailylimit reached")
                
                # check that all keys haven't reached the daily limit
                endless_loop_counter = len(self.vt_keys)
                current_counter = 0
                while self.vt_key_limit_status[current_key_index] == "dailylimit":
                    if current_counter == endless_loop_counter:
                        break
                        self.keys_maxed_out = True
                    else: 
                        current_counter += 1    
                
                # if last key, wait minute between now and first key start time
                if current_key_index == len(self.vt_keys) - 1:
                    print("reached last key, waiting for timer to restart")
                    while time.time() - self.vt_key_limit_minute_start[0] < 61:
                        time.sleep(1)
                        
                # rotate key
                current_key_index = current_key_index + 1 % len(self.vt_keys)
                print("rotating keys, new key index: " + str(current_key_index))