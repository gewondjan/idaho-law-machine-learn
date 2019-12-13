# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 21:23:30 2019

@author: Ryan
"""

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing as pp

from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

bill_data = pd.read_csv("prepared_data.csv")
#Remove the row number
bill_data = bill_data.drop(["Unnamed: 0"], axis=1)

# Label Encode!!
le = pp.LabelEncoder()
bill_data['Made_Law'] = le.fit_transform(bill_data['Made_Law'])
bill_data['Revised_SoP'] = le.fit_transform(bill_data['Revised_SoP'])
bill_data['Amended'] = le.fit_transform(bill_data['Amended'])
bill_data['Started_House_Or_Senate'] = le.fit_transform(bill_data['Started_House_Or_Senate'])
bill_data['Summary_Length'] = le.fit_transform(bill_data['Summary_Length'])
#bill_data['cost'] = le.fit_transform(bill_data['cost'])
bill_data['No_Cost'] = le.fit_transform(bill_data['No_Cost'])

# Convert to target and data sets
targets = bill_data.Made_Law.values
data = bill_data.drop(["Made_Law"], axis=1).values


data_train, data_test, target_train, target_test_expected = train_test_split(data, targets, train_size=.70)


myClassifier = GradientBoostingClassifier(n_estimators=1000)
myClassifier.fit(data_train, target_train)
target_test_actual_GBM = myClassifier.predict(data_test)


def getAccuracy(expected, actual):
    numberThatAreCorrect = 0
    for i in range(len(expected)):
        if expected[i] == actual[i]:
            numberThatAreCorrect = numberThatAreCorrect + 1
    
    return numberThatAreCorrect / len(expected)

print(getAccuracy(target_test_expected, target_test_actual_GBM))

myClassifierKNN = KNeighborsClassifier(n_neighbors=3)
myClassifierKNN.fit(data_train, target_train)
target_test_actual_KNN = myClassifierKNN.predict(data_test)

print(getAccuracy(target_test_expected, target_test_actual_KNN))

myClassifierNB = GaussianNB()
myClassifierNB.fit(data_train, target_train)
target_test_actual_NB = myClassifierNB.predict(data_test)

print(getAccuracy(target_test_expected, target_test_actual_NB))



