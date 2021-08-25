-------------------------
CM3203 Individual Project
Izabele Bauzyte - 1941278
README.txt
-------------------------

"UnitTesting" contains the testing scripts for various parts of the project

"meta_classifier_creation.py" contains code for the training and creation of the meta classifier from sklearn called StackingClassifier

"metric_extraction.py" is a script that extracts the confusion matrix as well as accuracy precision and recall data from a csv file containing both the actual 'malicious' column and the 'Prediction' column

"tp_run.py" runs the TweetProcessor collection class using different filter hashtags. The VirusTotal API key and the Tweepy Consumer key and secret, and may not function when used. 

"TweetProcessor.py" is a class used in the tp_run.py script and requires as inputs: tweepy consumer key, tweepy consumer secret, filter, VirusTotal keys, and the collection batch size.  