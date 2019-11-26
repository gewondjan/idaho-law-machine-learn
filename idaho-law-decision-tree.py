# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 13:54:01 2019

@author: Ryan Gewondjan, Keaton Parkinson, Caleb Baird
"""


# Read in the data and preprossess
###########################################################

import pandas

law_data = pandas.read_csv("../idaho-law-machine-learn/template_csv_for_idaho_bills.csv")# This encoding might be necessary: encoding="ISO-8859-1")

# Transform the first column to 'H' or 'S'

# Reduce the topics column to the set of highest priority topics

# Get Fiscal Note length make 3 buckets

# Categorize session introduction into percentiles (4 percentiles)







print(law_data)







# Run Built-in Decision Tree Algorithm
############################################################

