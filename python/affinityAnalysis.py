#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 15:10:59 2022

@author: tom
"""

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

import dataPrep



df = pd.read_csv('/home/tom/ResearchData/Coffee/receipts-all.csv')



'''
Data Wrangling for main sales data
'''


df = dataPrep.prep(df)


'''
Data preperation for analysis
'''


df = df.explode('Omschrijving').reset_index().groupby(['Bon nummer', 'Omschrijving']).Omschrijving.count()
df = df.to_frame()
df.rename(columns={'Omschrijving':'Aantal'}, inplace=True)
df = df.reset_index()


df.dropna(subset=['Bon nummer'], inplace=True)
df[['Bon nummer', 'Omschrijving']] = df[['Bon nummer', 'Omschrijving']].astype('str')

# Create a basket for every receipt with categorical encoding (in basket = 1, not in basket = 0)
basket = df.groupby(['Bon nummer', 'Omschrijving'])['Aantal'].sum().unstack().reset_index().fillna(0).set_index('Bon nummer')

def encode_units(x):
    if x <= 0:
        return 0
    elif x >= 1:
        return 1

basket = basket.applymap(encode_units)

basket = basket[(basket > 0).sum(axis=1) >= 2]


'''
Affinity Analysis with apriori
'''



freq_items_apriori = apriori(basket, min_support=0.05, use_colnames=True)

rules_apriori = association_rules(freq_items_apriori, metric='lift', min_threshold=1)
rules_apriori.sort_values('lift', inplace=True, ascending=False)
print(rules_apriori)

























