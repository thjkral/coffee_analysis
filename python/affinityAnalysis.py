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



df = pd.read_csv('/home/tom/ResearchData/Coffee/receipts-all.csv')



'''
Data Wrangling for main sales data
'''


# Drop empty or useless columns and add datetime
df.drop(['Bon soort', 'POS', 'Winkel', 'Naam medewerker', 'Naam klant', 'Klant contacten', 'Status'], axis=1, inplace=True)
df['Datum'] = pd.to_datetime(df['Datum'])

def comma_changer(text): # When a product name contains a comma, this function changes it to a colon
  text = list(text)
  quote_counter = 0
  for i,char in enumerate(text):
    if char == '"':
      quote_counter+=1
    elif char == ",":
      if quote_counter%2 == 1:
        text[i] = ":"
  return("".join(text))


def extendOrder(order): # Multiply products bought more than once
    products = order.split(', ')
    new_list = []
    
    for p in products:
        amount = p.split('x ')[0]
        amount = int(amount.strip())
        
        prod = p.split('x ')[1]
        
        #print(f'Prod= {prod}, Amount= {amount}')
        
        counter = 1
        while counter <= amount:
            new_list.append(prod)
            counter += 1
    
    #return ','.join(new_list)
    return new_list

df['Omschrijving'] = df['Omschrijving'].apply(lambda x: comma_changer(x))
df['Omschrijving'] = df['Omschrijving'].apply(lambda x: extendOrder(x))


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

























