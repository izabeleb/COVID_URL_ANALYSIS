# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:21:46 2021

@author: Izabele
"""

import csv
from langdetect import detect

with open('csvfile.csv', 'r', encoding="utf-8-sig", newline='') as inputf, open('texts_predictions.csv', 'w', encoding="utf-8-sig", newline='') as outputf:
            
    reader = csv.reader(inputf)
    writer = csv.writer(outputf)
    
    for row in reader:
        
        try:
            
            detection = detect(row[0])            
            print(detection)
            writer.writerow([detection, row[1]])
            
        except:
            pass