# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 13:54:01 2019

@author: Ryan Gewondjan, Keaton Parkinson, Caleb Baird
"""


# Read in the data and preprossess
###########################################################

import pandas as pd

law_data = pandas.read_csv("../idaho-law-machine-learn/template_csv_for_idaho_bills.csv")# This encoding might be necessary: encoding="ISO-8859-1")

# Transform the first column to 'H' or 'S'

# Reduce the topics column to the set of highest priority topics

# Load the list of important topics
topics_data = pd.read_csv("topics.csv")

# Make it uppercase to avoid case problems
law_data["Topics (~ delimiter)"] = law_data["Topics (~ delimiter)"].str.upper()
topics_data.Topics = topics_data.Topics.str.upper()

topics = topics_data.Topics

for (index, law_topics) in enumerate(law_data["Topics (~ delimiter)"]):
    possible_topics = law_topics.split('~')
    possible_topic_indexs = []
    for possible_topic in possible_topics:
        for (i, topic) in enumerate(topics):
            if possible_topic == topic:
                possible_topic_indexs.append(i)
                break
    law_data["Topics (~ delimiter)"][index] = topics[min(possible_topic_indexs)]

# Get Fiscal Note length make 3 buckets
# print(law_data["Fiscal Note"])
law_data.cost = law_data["Fiscal Note"]
fiscal_note_lengths = law_data["Fiscal Note"].str.len()
mean = statistics.mean(law_data["Fiscal Note"].str.len())
stdev = statistics.stdev(law_data["Fiscal Note"].str.len())
for (index, length) in enumerate(fiscal_note_lengths):
    if length < mean - stdev:
        cost = "Low"
    elif length < mean + stdev:
        cost = "Medium"
    else:
        cost = "High"
    law_data.cost[index] = cost
    law_data.drop("Fiscal Note", axis=1, inplace=True)

print(law_data.cost)

# Categorize session introduction into percentiles (4 percentiles)







print(law_data)







# Run Built-in Decision Tree Algorithm
############################################################

