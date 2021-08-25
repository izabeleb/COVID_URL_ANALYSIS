
import pandas as pd
import numpy as np
import joblib
import csv
import sys

from DataProcessor import DataProcessor

def main():
    
    inputfile = sys.argv[1]
    account_json = None
    
    try:
        account_json = sys.argv[2]
    except:
        pass
    
    outputfile = inputfile.split('.')[0] + "_OUTPUT." + inputfile.split('.')[1]
    inputfile_with_predictions = inputfile.split('.')[0] + "_PREDICTIONS." + inputfile.split('.')[1]
    
    if account_json is None:
        processor = DataProcessor(inputfile, outputfile, False, None, None)
        processor.run()
    else:  
        processor = DataProcessor(inputfile, outputfile, True, account_json, None)
        processor.run()
        
    data = read_csv(outputfile)
    data = clean_data(data)

    classifier = joblib.load("sclf_trained_model.pkl")
    
    predictions = classifier.predict(data)
    
    with open(inputfile, 'r', encoding="utf-8-sig", newline='') as inputf, open(inputfile_with_predictions, 'w', encoding="utf-8-sig", newline='') as outputf:
        writer = csv.writer(outputf)
        reader = csv.reader(inputf)
        
        header = next(reader) #header
        header.append('Prediction')
        writer.writerow(header)
        
        for prediction in predictions:
        
            row = next(reader)
            row.append(prediction)
    
            writer.writerow(row)
            
def read_csv(filename):
    return pd.read_csv(filename, sep=',', header=0)

def clean_data(data):
    
    data = data._get_numeric_data()
    data.replace(["NaN", 'NaT'], np.nan, inplace = True)
    data = data.dropna()
    data = data.astype('float')
    return data

if __name__ == "__main__":
    main()