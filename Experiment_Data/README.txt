-------------------------
CM3203 Individual Project
Izabele Bauzyte - 1941278
README.txt
-------------------------

This directory contains the data results from the experiments conducted during the project.

-------------------------

"feature_importance_fact_checking.xlsx" contains a ranking of feature importance extracted from the RandomForestClassifier during the misinformation classification section of the project.

"feature_importance_malicious_benign.xlsx" contains a ranking of feature importance extracted from the RandomForestClassifier during the malicious/benign URL classification section of the project.

"hashtag_analysis.xlsx" contains detailed information on the number of VirusTotal positives returned per hashtag during daily collections, as well as some chart visuals showing malicious percentage of hashtags used in the report. 

"hashtag_collections.csv" contains information on the number of tweets collected by day and hashtag type.

"language_malicious_benign.xlsx" contains language summaries of malicious and benign tweets, including language malicious percentage charts used in the report.

"model_tuning_data.xlsx" contains 5 different tabs for some of the model tunings conducted, and also includes some tuning visuals used in the report.

"processed_file_26000_samples.csv" contains the data of the roughly 26,000 processed samples used as training and testing input for all the classifiers being evaluated. This data contains 54 features and the 'MALICIOUS' class label.

"processed_file_26000_samples_statistical_analysis.xlsx" contains the results of statistical analysis conducted separately on the malicious and benign processed samples. This includes measures of dataset minimum, maximum, mean, and standard deviation for all features, as well as several tabs containing overviews. 

"validation_set_runtimes.xlsx" contains 10 prediction runtimes recorded during a validation set run of 1000 samples. 
