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

law_data = pd.read_csv("legislation.csv")# This encoding might be necessary: encoding="ISO-8859-1")

# Drop all Error Rows
errorRows = []
for bill_index, bill_row in law_data.iterrows():

    # Drop rows that have an improperly formed Legislative Session?
    if isinstance(bill_row["Legislative_Session"], float) or bill_row["Legislative_Session"] == "" or bill_row["Legislative_Session"] == "ERROR: AttributeError":
        errorRows.append(bill_index)

    # Drop Error Rows that have a non year in Legislative Year
    try:
        int(bill_row["Legislative_Year"])
    except:
        errorRows.append(bill_index)

    # Drop rows that don't have any topics
    if (bill_row["Topics"] == "" or isinstance(bill_row["Topics"], float)):
        errorRows.append(bill_index)


    # Drop rows that have errors instead of dates in introduction dates
    try:
        pd.to_datetime(bill_row["Introduction_Date"])
    except:
        errorRows.append(bill_index)
        
    # Drop rows that have a committee name that doesn't end with "committee"
    committeeName = bill_row["Starting_Committee"]
    committeeWordsArray = committeeName.upper().split()
    if committeeWordsArray[-1] != "COMMITTEE":
        errorRows.append(bill_index)
        
    # Drop rows that have an error message in the Legislative session
        
# If there is more than one error for each row, remove the duplicates
errorRows = set(errorRows)
# Drop the Error Rows
law_data = law_data.drop(errorRows, axis=0)

# Remove commas from committee names

def removeCommas(committeeName):
    committeeNameArray = committeeName.split(',')
    return "".join(committeeNameArray)
law_data["Starting_Committee"] = law_data["Starting_Committee"].apply(lambda committee: removeCommas(committee))


#print(law_data["Starting_Committee"].unique())
#print(law_data["Starting_Committee"].value_counts())

# Transform the first column to 'H' or 'S'
pd.set_option('display.max_columns', None)
list(law_data.columns)
law_data['Started_House_Or_Senate'] = law_data['Legislation_Code'].str[0]
law_data.drop('Legislation_Code', axis=1, inplace=True)

# Label Encoding the Starting Committee (1 of 18)

le = pp.LabelEncoder()
law_data['Starting_Committee'] = le.fit_transform(law_data['Starting_Committee'])


# Label Encoded Sponsor Contact Party (R, D, or not legislator)
# TODO: ADD THE SPONSOR CONTACT PARTY
#law_data['Sponsor Contact Party (R, D, or not legislator)'] = le.fit_transform(law_data['Sponsor Contact Party (R, D, or not legislator)'])

# Reduce the topics column to the set of highest priority topics

# Load the list of important topics
topics_data = pd.read_csv("topics.csv")

# Make it uppercase to avoid case problems
law_data["Topics"] = law_data["Topics"].str.upper()
topics_data.Topics = topics_data.Topics.str.upper()
topics_data.Keywords = topics_data.Keywords.str.upper()

topics = topics_data.Topics
keywords = topics_data.Keywords

hot_topic_column = []
# Loop through each bill
for (index, law_topics_row) in enumerate(law_data["Topics"]):
    hot_topic = False
    bill_topics = [x.strip() for x in law_topics_row.split('~')]

    # Loop through each topic of that bill
    for bill_topic in bill_topics:

        # Loop through the list of Priority topics
        for (i, (priority_topic, topic_keywords)) in enumerate(zip(topics, keywords)):
            # Check to see if the bill topic matches the priority topic or one of the keywords.
            individual_keywords = [x.strip() for x in topic_keywords.split('~')]
            if bill_topic == priority_topic:
                hot_topic = True
                break
            else:
                for keyword in individual_keywords:
                    if bill_topic == keyword:
                        hot_topic = True
                        break
            if hot_topic:
                break
        if hot_topic:
            break
    hot_topic_column.append(1 if hot_topic else 0)
law_data.insert(0, "Hot_Topic", hot_topic_column)
htt = 0
htf = 0
for ht in law_data.Hot_Topic:
    if ht == 1: htt += 1
    else: htf += 1


# Get Fiscal Note length make 3 buckets
fiscal_note_lengths = law_data["Fiscal_Note"].str.len()
mean = statistics.mean(fiscal_note_lengths)
stdev = statistics.stdev(fiscal_note_lengths)
cost_column = []
for (index, length) in enumerate(fiscal_note_lengths):
    if length < mean - stdev:
        cost_column.append('Low')
    elif length < mean + stdev:
        cost_column.append('Medium')
    else:
        cost_column.append('High')
law_data.insert(0, 'cost', cost_column)
# law_data.rename(columns = {'Fiscal_Note':'cost'}, inplace = True)

# Categorize session introduction into percentiles (4 percentiles)

## 1. Read in the Session Date CSV and Convert to a date format that we can work with
session_dates_data = pd.read_json('./IDLegPull_session_dates.json')

session_dates_data["Session_Convened"] = pd.to_datetime(session_dates_data["Session_Convened"])
session_dates_data["Session_Adjourned"] = pd.to_datetime(session_dates_data["Session_Adjourned"])

law_data["Introduction_Date"] = pd.to_datetime(law_data["Introduction_Date"])

## 2. Trim down the Legislative Session Name Long to the format: Regular Session - 2019 (Type Session - Year)
def removeFirstWordInString(sessionName):
    if not isinstance(sessionName, str):
        print(sessionName)
    assert(isinstance(sessionName, str))
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
rowsWithoutValidKey = []
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
        rowsWithoutValidKey.append(bill_index)
        print(bill_row["Legislative_Session_Key"])
        startDateArray.append("NO MATCH IN SESSION DATES CSV")
        endDateArray.append("NO MATCH IN SESSION DATES CSV")

law_data.insert(0, "session_convened_date", startDateArray)
law_data.insert(0, "session_adjourned_date", endDateArray)

law_data = law_data.drop(rowsWithoutValidKey, axis=0)


## 4. Now it is as if the session start and end dates were included in the original CSV
## proceed to perform the calculation for percentile

session_date_percentiles = []
for bill_index, bill_row in law_data.iterrows():
    if bill_row["Legislative_Session"] == "Extraordinary Session":
        session_date_percentiles.append(0)
        print("{} - start: {} - end: {}".format(bill_row["Legislative_Session"], bill_row["session_convened_date"], bill_row["session_adjourned_date"]))
        continue
    numDaysInSession = None
    try:
        numDaysInSession = (bill_row["session_adjourned_date"] - bill_row["session_convened_date"]).days
    except:
        print(bill_row["session_adjourned_date"])
        print(bill_row["session_convened_date"])
        raise Exception("PROBLEM")
    numDaysInPercentile = numDaysInSession // 4 # Since we always round down, this will cause some error in our data, but we're considering it insignificant for now.
    numDaysIntoSessionBillIsIntroduced = (bill_row["Introduction_Date"] - bill_row["session_convened_date"]).days
    percentile = math.ceil(numDaysIntoSessionBillIsIntroduced / numDaysInPercentile)
    session_date_percentiles.append(percentile)

law_data.insert(0, "session_date_percentile", session_date_percentiles)

## 5. Remove intermediate columns that are no longer needed
law_data = law_data.drop(["session_adjourned_date", "session_convened_date", "Legislature", "Fiscal_Note",\
                          "Statement_of_Purpose", "Fiscal_Note_Length", "Legislation_Name_Long", "Summary",\
                          "Legislative_Session", "Bill_Sponsors", "Topics", "Legislation_Name_Medium",\
                          "Legislative_Session_Name_Long", "Legislative_Session_Key", "Legislative_Year",\
                          "Introduction_Date", "Legislation_Name_Short", "Legislation_Code_Plus", "RS_Number"], axis=1)


# print(law_data)
# random.shuffle(law_data)
print(law_data)

# Run Built-in Decision Tree Algorithm
############################################################



