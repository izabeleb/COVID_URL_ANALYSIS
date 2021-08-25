# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 11:26:31 2021

@author: Izabele
"""
import requests
import json

def main():
    apikey = ""
    url = "17ebook.com"
    
    print(vt_api_call(apikey, url))

def vt_api_call(apikey, url):
    
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
        print(json.dumps(r.json()))
        try:
            
            positives = r.json()["positives"]
            total = r.json()["total"]
        except:
            print("ERROR: ", request_status, url_status, r.json())
        
        
    return [request_status, url_status, positives, total, scan_id]

main()