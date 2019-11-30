# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 13:54:01 2019

@author: Ryan Gewondjan, Keaton Parkinson, Caleb Baird
"""


# Read in the data and preprossess
###########################################################

import pandas as pd
import math

law_data = pd.read_csv("template_csv_for_idaho_bills.csv")# This encoding might be necessary: encoding="ISO-8859-1")

# Transform the first column to 'H' or 'S'

# Reduce the topics column to the set of highest priority topics

# Get Fiscal Note length make 3 buckets

# Categorize session introduction into percentiles (4 percentiles)

## 1. Read in the Session Date CSV and Convert to a date format that we can work with
session_dates_data = pd.read_csv("../idaho-law-machine-learn/session_dates_csv_template.csv")

session_dates_data["Date_convened"] = pd.to_datetime(session_dates_data["Date_convened"])
session_dates_data["Date_adjourned"] = pd.to_datetime(session_dates_data["Date_adjourned"])
law_data["Session Introduction Date"] = pd.to_datetime(law_data["Session Introduction Date"])

## 2. Trim down the Legislative Session Name Long to the format: Regular Session - 2019 (Type Session - Year)
def getSessionNameOutOfLongSessionName(sessionName):
    sessionNameArray = sessionName.split()
    # need to append a dummy value, so we can get the element on the very end of the array
    sessionNameArray.append("DummyValue")
    sessionNameArray = sessionNameArray[-5:-1]
    return " ".join(sessionNameArray)

law_data["Legislative Session Name"] = \
law_data["Legislative Session Name Long"].apply(lambda sessionName: getSessionNameOutOfLongSessionName(sessionName))


## 3. Add columns to the law_data that correspond to the session start date and end date that are associated with the bill.
startDateArray = []
endDateArray = []
for bill_index, bill_row in law_data.iterrows():
    foundMatch = False
    for session_date_index, session_date_row in session_dates_data.iterrows():
        if session_date_row["Session_name"] == bill_row["Legislative Session Name"]:
            startDateArray.append(session_date_row["Date_convened"])
            endDateArray.append(session_date_row["Date_adjourned"])
            foundMatch = True
    if not foundMatch:
        startDateArray.append("NO MATCH IN SESSION DATES CSV")
        endDateArray.append("NO MATCH IN SESSION DATES CSV")

law_data["session_convened_date"] =  startDateArray
law_data["session_adjourned_date"] = endDateArray


## 4. Now it is as if the session start and end dates were included in the original CSV
## proceed to perform the calculation for percentile

session_date_percentiles = []
for bill_index, bill_row in law_data.iterrows():
    numDaysInSession = (bill_row["session_adjourned_date"] - bill_row["session_convened_date"]).days
    numDaysInPercentile = numDaysInSession // 4 # Since we always round down, this will cause some error in our data, but we're considering it insignificant for now.
    numDaysIntoSessionBillIsIntroduced = (bill_row["Session Introduction Date"] - bill_row["session_convened_date"]).days
    percentile = math.ceil(numDaysIntoSessionBillIsIntroduced / numDaysInPercentile)
    session_date_percentiles.append(percentile)
    
law_data["session_date_percentile"] = session_date_percentiles

## 5. Remove intermediate columns that are no longer needed
law_data.drop("session_adjourned_date", axis=1)
law_data.drop("session_convened_date", axis=1)
law_data.drop("Legislative Session Name", axis=1)
law_data.drop("Legislative Session Name Long", axis=1)


print(law_data)


# Run Built-in Decision Tree Algorithm
############################################################

