# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 13:54:01 2019

@author: Ryan Gewondjan, Keaton Parkinson, Caleb Baird
"""


# Read in the data and preprossess
###########################################################

import pandas as pd
import math
import statistics
from sklearn import preprocessing as pp

law_data = pd.read_csv("template_csv_for_idaho_bills.csv")# This encoding might be necessary: encoding="ISO-8859-1")

# Transform the first column to 'H' or 'S'
pd.set_option('display.max_columns', None)
list(law_data.columns)
law_data['Bill Code Starts with H or S'] = law_data['Bill Code (starts with H or S)'].str[0]
law_data.drop('Bill Code (starts with H or S)', axis=1, inplace=True)

# Label Encoding the Starting Committee (1 of 18)

le = pp.LabelEncoder()
law_data['Starting Committee (1 of 18)'] = le.fit_transform(law_data['Starting Committee (1 of 18)'])

# Label Encoded Sponsor Contact Party (R, D, or not legislator)

law_data['Sponsor Contact Party (R, D, or not legislator)'] = le.fit_transform(law_data['Sponsor Contact Party (R, D, or not legislator)'])

# Reduce the topics column to the set of highest priority topics

# Load the list of important topics
topics_data = pd.read_csv("topics.csv")

# Make it uppercase to avoid case problems
law_data["Topics (~ delimiter)"] = law_data["Topics (~ delimiter)"].str.upper()
topics_data.Topics = topics_data.Topics.str.upper()

topics = topics_data.Topics

for (index, law_topics) in enumerate(law_data["Topics (~ delimiter)"]):
    possible_topics = law_topics.split('~')
    possible_topic_indexes = []
    for possible_topic in possible_topics:
        for (i, topic) in enumerate(topics):
            if possible_topic == topic:
                possible_topic_indexes.append(i)
                break
    topic = 'Other' if len(possible_topic_indexes) == 0 else topics[min(possible_topic_indexes)]
    law_data.loc[index, "Topics (~ delimiter)"] = topic

# Get Fiscal Note length make 3 buckets
# print(law_data["Fiscal Note"])
fiscal_note_lengths = law_data["Fiscal Note"].str.len()
mean = statistics.mean(fiscal_note_lengths)
stdev = statistics.stdev(fiscal_note_lengths)
for (index, length) in enumerate(fiscal_note_lengths):
    if length < mean - stdev:
        law_data.loc[index, "Fiscal Note"] = "Low"
    elif length < mean + stdev:
        law_data.loc[index, "Fiscal Note"] = "Medium"
    else:
        law_data.loc[index, "Fiscal Note"] = "High"
law_data.rename(columns = {'Fiscal Note':'cost'}, inplace = True)

# Categorize session introduction into percentiles (4 percentiles)

## 1. Read in the Session Date CSV and Convert to a date format that we can work with
session_dates_data = pd.read_json('./IDLegPull_session_dates.json')

session_dates_data["Session_Convened"] = pd.to_datetime(session_dates_data["Session_Convened"])
session_dates_data["Session_Adjourned"] = pd.to_datetime(session_dates_data["Session_Adjourned"])

law_data["Session Introduction Date"] = pd.to_datetime(law_data["Session Introduction Date"])

## 2. Trim down the Legislative Session Name Long to the format: Regular Session - 2019 (Type Session - Year)
def removeFirstWordInString(sessionName):
    sessionNameArray = sessionName.split()
    sessionNameArray = sessionNameArray[1:]
    return " ".join(sessionNameArray)

law_data["Legislative_Session"] = \
law_data["Legislative_Session"].apply(lambda sessionName: removeFirstWordInString(sessionName))

sessionNameKeyToSessionDatesFile = []
for bill_index, bill_row in law_data.iterrows():
    sessionNameKeyToSessionDatesFile.append(str(bill_row["Legislative_Year"]) + " " +  bill_row["Legislative_Session"])

law_data.insert(0, "Legislative_Session_Key", sessionNameKeyToSessionDatesFile)    

## 3. Add columns to the law_data that correspond to the session start date and end date that are associated with the bill.
startDateArray = []
endDateArray = []
for bill_index, bill_row in law_data.iterrows(): 
    foundMatch = False
    for session_date_index, session_date_row in session_dates_data.iterrows():
        if session_date_row["Session_Name"] == bill_row["Legislative_Session_Key"]:
            startDateArray.append(session_date_row["Session_Convened"])
            endDateArray.append(session_date_row["Session_Adjourned"])
            foundMatch = True
            break
    if not foundMatch:
        # Change this to an exception being thrown with enough information to know whats happening.
        startDateArray.append("NO MATCH IN SESSION DATES CSV")
        endDateArray.append("NO MATCH IN SESSION DATES CSV")

law_data.insert(0, "session_convened_date", startDateArray)
law_data.insert(0, "session_adjourned_date", endDateArray)

#law_data["session_convened_date"] = pd.to_datetime(law_data["session_convened_date"])
#law_data["session_adjourned_date"] = pd.to_datetime(law_data["session_adjourned_date"])

## 4. Now it is as if the session start and end dates were included in the original CSV
## proceed to perform the calculation for percentile

session_date_percentiles = []
for bill_index, bill_row in law_data.iterrows():
    numDaysInSession = (bill_row["session_adjourned_date"] - bill_row["session_convened_date"]).days
    numDaysInPercentile = numDaysInSession // 4 # Since we always round down, this will cause some error in our data, but we're considering it insignificant for now.
    numDaysIntoSessionBillIsIntroduced = (bill_row["Session Introduction Date"] - bill_row["session_convened_date"]).days
    percentile = math.ceil(numDaysIntoSessionBillIsIntroduced / numDaysInPercentile)
    session_date_percentiles.append(percentile)
    
law_data.insert(0, "session_date_percentile", session_date_percentiles)

## 5. Remove intermediate columns that are no longer needed
law_data = law_data.drop(["session_adjourned_date", "session_convened_date",\
                          "Legislative_Session",\
                          "Session Introduction Date"], axis=1)

print(law_data)


# Run Built-in Decision Tree Algorithm
############################################################
