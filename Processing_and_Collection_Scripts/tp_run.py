# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 00:25:41 2021

@author: Izabele
"""

import time
from datetime import datetime

def main():
    
    """
        This script can be run as a batch file for automatic tweet collection
        throughout the day
    """
    
    from TweetProcessor import TweetProcessor
    
    consumer_key = ''
    consumer_secret = ''
    tweepy_base_filter = "Filter:links -Filter:retweets"
    
    hashtags = [
            "#covid-19", "#covid19", "#covid", "#coronavirus", "#corona",
            "#covid_19"
            ]
    
    vt_keys = [""]
    batch_size = 5000
    
    for i in range(len(hashtags)):
        
        try:
            tweepy_filter = hashtags[i] + " " + tweepy_base_filter
            print("starting pull with this filter: " + str(tweepy_filter))
            
            tp = TweetProcessor(consumer_key, consumer_secret,
                    tweepy_filter, vt_keys, batch_size)
        
            tp.run()

        except Exception as e: 
            with open("tweetProcessorLog.txt", "a") as file:
                file.write("\n" + str(datetime.now()) + ", error: " + str(e))
                
                
            if e != "Twitter error response: status code = 429":
                raise e

                
            print("ERROR OCCURED: waiting for 15 minutes to avoid hitting tweepy request limit")
            print(e)
            time.sleep(15 * 60)
            


if __name__ == "__main__":
    main()