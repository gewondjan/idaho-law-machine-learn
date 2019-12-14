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
#from xgboost import XGBClassifier
#from xgboost import plot_importance
from matplotlib import pyplot
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

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

#print(bill_data)


# Convert to target and data sets
targets = bill_data.Made_Law.values
data = bill_data.drop(["Made_Law"], axis=1).values

data_train, data_test, target_train, target_test_expected = train_test_split(data, targets, test_size=.20)


def getAccuracy(expected, actual):
    numberThatAreCorrect = 0
    for i in range(len(expected)):
        if expected[i] == actual[i]:
            numberThatAreCorrect = numberThatAreCorrect + 1
    
    return round((numberThatAreCorrect / len(expected)) * 100, 2)

def runMachineLearningAlgorithm(classifierArray, expected, training_data, training_targets, testing_data):
    for classifier in classifierArray:
        classifier.fit(training_data, training_targets)
        target_test_actual = classifier.predict(testing_data)
        print("{}: {}%".format(type(classifier), getAccuracy(expected, target_test_actual)))
    return


classifiers = []
classifiers =[GaussianNB(), KNeighborsClassifier(), GradientBoostingClassifier(), MLPClassifier(), MLPClassifier(hidden_layer_sizes= [3, 2]), DecisionTreeClassifier()]

runMachineLearningAlgorithm(classifiers, target_test_expected, data_train, target_train, data_test)




#xgBoostClassifier = XGBClassifier()
#xgBoostClassifier.fit(data_train, target_train)
#plot_importance(xgBoostClassifier)
#pyplot.show()

