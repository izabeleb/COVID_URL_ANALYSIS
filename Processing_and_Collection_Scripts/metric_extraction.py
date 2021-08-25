
import csv
import sys

def main():
    
    inputfile = sys.argv[1]
        
    with open(inputfile, 'r', encoding="utf-8-sig", newline='') as inputf:
        
        reader = csv.reader(inputf)
        
        total_samples = 0
        fp = 0
        tp = 0
        fn = 0
        tn = 0
        
        header = next(reader) #header

        for row in reader:
            
            total_samples += 1
            actual = int(row[header.index('malicious')])
            predicted = int(row[header.index('Prediction')])
            
            if actual==0 and predicted==0:
                tn+=1
            elif actual==0 and predicted==1:
                fp+=1
            elif actual==1 and predicted==1:
                tp+=1
            elif actual==1 and predicted==0:
                fn+=1
         
        print("total samples: \t" + str(total_samples))
        print()
        print("false positives: \t" + str(fp))
        print("true positives: \t" + str(tp))
        print("false negatives: \t" + str(fn))
        print("true negatives: \t" + str(tn))
        print()
        print("accuracy: \t" + str((tp+tn)/(fp+tp+fn+tn)))
        print("precision: \t" + str((tp)/(tp+fp)))
        print("recall: \t" + str((tp)/(tp+fn)))
    
if __name__ == "__main__":
    main()
    