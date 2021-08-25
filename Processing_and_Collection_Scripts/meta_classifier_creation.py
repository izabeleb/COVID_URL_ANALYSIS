

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 20:38:21 2021

@author: Izabele
"""

import pandas as pd
import numpy as np

from sklearn import tree

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier

import graphviz

import joblib

def main():
    filename = "FINAL_PROCESSED_FILE.csv"
    data = read_csv(filename)
    data = clean_data(data)
    test_size = 0.2
    x,y = get_xy_data(data)

    dt_clf = DecisionTreeClassifier(max_depth=10, splitter='best')
    #rf_clf = RandomForestClassifier(n_estimators=17, max_depth=18)
    rf_clf = RandomForestClassifier()
    mlp_clf = MLPClassifier(learning_rate='constant', solver='adam', activation='relu')
    gnb_clf = GaussianNB()
    #svc_clf = SVC(kernel='rbf', C=100)
    knn_clf = KNeighborsClassifier(n_neighbors=2, weights='distance', algorithm='auto', p=1)
    
    lr = LogisticRegression() # meta classifier
    
    sclf = StackingClassifier(
            estimators= [('dt', dt_clf), 
                         ('rf', rf_clf), 
                         ('mlp', mlp_clf),
                         ('gnb', gnb_clf), 
                         #('svc', svc_clf),
                         ('knn', knn_clf)], 
            final_estimator=lr)
    
    
    #classifier_array = [dt_clf, rf_clf, mlp_clf, gnb_clf, svc_clf, knn_clf, sclf]
    classifier_array = [dt_clf, rf_clf, mlp_clf, gnb_clf, knn_clf, sclf]
    labels = [clf.__class__.__name__ for clf in classifier_array] 
    
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = test_size, random_state = 80)

    for model, label in zip(classifier_array, labels):
        
        classifier = model.fit(x_train, y_train)
        y_pred = classifier.predict(x_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print("%s, %0.4f, %0.4f, %0.4f, %0.4f" % (label, accuracy, precision, recall, f1)) 
        
        if label=='StackingClassifier':
            joblib.dump(sclf, 'sclf_trained_model.pkl')
        
#        try:
#            get_feature_importance(data.columns, classifier)
#        except:
#            print("feature importance not available")    
#        
#        print()
        
#        if label=="DecisionTreeClassifier":
#            create_graph(model, data, 'DecisionTreeMisinfo')
#            
#        if label=="RandomForestClassifier":
#            #create_graph_forest(model, data, 'RandomForestMisinfo')
        
def create_graph(classifier, data, classifier_name):
    
    str_classes = ['Benign' if item==0 else 'Malicious' for item in classifier.classes_]
    
    dot_data = tree.export_graphviz(classifier, out_file=None, 
                                    feature_names=data.columns[0:len(data.columns) - 1],
                                    class_names = str_classes, filled=True, 
                                    rounded=True, special_characters=True)
    
    
    
    graph = graphviz.Source(dot_data)
    graph.render(classifier_name, view=True)
    
def create_graph_forest (rf, data, classifier_name):
    
    str_classes = ['Malicious' if item==1 else 'Benign' for item in rf.classes_]
    
    index = 0
    for estimator in rf.estimators_:
        
        dot_data = tree.export_graphviz(estimator, out_file=None, 
                                        feature_names=data.columns[0:len(data.columns) - 1],
                                        class_names = str_classes, filled=True, 
                                        rounded=True, special_characters=True)
        
        graph = graphviz.Source(dot_data)
        graph.render(classifier_name+str(index), view=True)
        index+= 1

    
def read_csv(filename):
    return pd.read_csv(filename, sep=',', header=0)

def get_feature_importance(data_columns, classifier):
        
    for name, importance in zip(data_columns, classifier.feature_importances_):
        #print(name, importance)
        print(importance)

def clean_data(data):
    
    data = data._get_numeric_data()
    data.replace(["NaN", 'NaT'], np.nan, inplace = True)
    data = data.dropna()
    return data

def get_xy_data(data):
    
    num_features = len(data.columns)
    x = data.values[:, 0:num_features - 1]    # features
    y = data.values[:, num_features - 1]      # target data
    
    x = x.astype('float')
    y = y.astype('float')

    return x,y


if __name__ == "__main__":

    main()