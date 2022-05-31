#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 15:49:09 2022

@author: tom
"""

import numpy as np
import pandas as pd


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
    
    #return(','.join(new_list))
    return new_list

def prep(df):

# Drop empty or useless columns and add datetime
    df.drop(['Bon soort', 'POS', 'Winkel', 'Naam medewerker', 'Naam klant', 'Klant contacten', 'Status'], axis=1, inplace=True)
    df['Datum'] = pd.to_datetime(df['Datum'])   
    
    df['Omschrijving'] = df['Omschrijving'].apply(lambda x: comma_changer(x))
    df['Omschrijving'] = df['Omschrijving'].apply(lambda x: extendOrder(x))
    
    return df

