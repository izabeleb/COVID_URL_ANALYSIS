
Izabele Bauzyte
May 2021
COVIDURLS

-------------------
OVERVIEW
-------------------

ModelPrediction.py is a tweet classification script that will classify samples as either malicious (1) or benign (0).
The model used in this script is trained on approximately 26,000 COVID19 related tweets collected during the month of March 2021.


-------------------
ARGUMENTS
-------------------

This script has one required argument which is the inputfile, and one optional argument of the google service account json (used for translation purposes).

This following example line will call the ModelPrediction script to classify all samples in the sample.csv file WITHOUT translating any non-english tweets into english first.

>	py ModelPrediction.py sample.csv 

This following example line will call the ModelPrediction script to classify all samples in the sample.csv file after translating non-english tweets into english, using a json file containing the google service account details for the translation API.

>	py ModelPrediction.py sample.csv [SERVICE_ACCOUNT_FILE].json

-------------------
EXPECTED INPUTS
-------------------

The inputfile is expected to contain a header with the following data points, order is irrelevant.

	text, created_at, retweet_count, favorite_count, verified, followers_count, friends_count, listed_count, favourites_count, statuses_count, user_created_at, url

Additionally, the inputfile can contain as many other fields as you like as long as the required fields are included, the additional fields will be simply ignored.


-------------------
FILE CREATION
-------------------

The script will create 2 files. 
The first is the output file, which will be titled [inputfile]_OUTPUT.csv, and will contain processed features of the tweet information, this is the data that will be used by the classifier to determine maliciousness.
The prediction file, titled [inputfile]_PREDICTION.csv will contain the original data included in the inputfile, along with an additional column which will have classifier predictions: 0 for benign and 1 for malicious

-------------------
SCRIPT FUNCTIONALITY
-------------------

In order for this script to function correctly, the files 'emolex_wordlevel_92.txt' (used for sentiment analysis) and 'sclf_trained_model.pkl' (trained classifier model) must be left intact in the same directory as the script.
