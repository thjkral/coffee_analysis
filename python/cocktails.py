#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:25:05 2022

@author: tom
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


os.chdir('/home/tom/ResearchData/Coffee')

df_w = pd.read_csv('receipts-all.csv', index_col='Bon nummer')
df_i = pd.read_csv('export_items.csv', skip_blank_lines=True)



'''
Data Wrangling for main sales data
'''

# Plot missing values
plt.figure(figsize=(15, 10))
sns.heatmap(df_w.isna(), cmap='viridis', yticklabels=False, cbar=False)
plt.title('Missing values before dropping columns', size=20)
#plt.show()
plt.close()

# Drop empty or useless columns and add datetime
df_w.drop(['Bon soort', 'POS', 'Winkel', 'Naam medewerker', 'Naam klant', 'Klant contacten', 'Status'], axis=1, inplace=True)
df_w['Datum'] = pd.to_datetime(df_w['Datum'])

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


df_w['Omschrijving'] = df_w['Omschrijving'].apply(lambda x: comma_changer(x))
df_w['Omschrijving'] = df_w['Omschrijving'].apply(lambda x: extendOrder(x))

# Plot missing values after cleaning
plt.figure(figsize=(10, 15))
sns.heatmap(df_w.isna(), cmap='viridis', yticklabels=False, cbar=False)
plt.title('Missing values after dropping columns', size=20)
#plt.show()
plt.close()



'''
Data wrangling for item category data
'''

# Drop unnessecary columns
df_i.drop(df_i.columns.difference(['Name', 'Category']), axis=1, inplace=True)

# Plot missing values
plt.figure(figsize=(10,15))
sns.heatmap(df_i.isna(), cmap='viridis', cbar=False, yticklabels=False)
plt.title('Missing values in category data')
#plt.show()
plt.close()

# Drop missing values
df_i = df_i[df_i['Name'].notna()]


# Make names the index to add categories later
df_i.set_index('Name', inplace=True)



'''
Analyzing cocktail data
'''
# Count all the sales
cocktail_counts = df_w.explode('Omschrijving').reset_index().groupby(['Omschrijving', 'Datum']).Omschrijving.count()
cocktail_counts = cocktail_counts.to_frame()
cocktail_counts.rename(columns={'Omschrijving':'Count'}, inplace=True)
cocktail_counts = cocktail_counts.reset_index()

def get_category(product): # Add categories to products
    try:
        return df_i.loc[product, 'Category']
    except KeyError:
        return 'no_category'
    except pd.IndexingError:
        return 'unique_item'

cocktail_counts['Category'] = cocktail_counts['Omschrijving'].apply(lambda x: get_category(x))
cocktail_counts = cocktail_counts[(cocktail_counts['Category'] == 'Cocktail') | (cocktail_counts['Category'] == 'Mocktail')]
cocktail_counts['Datum'] = cocktail_counts['Datum'].dt.strftime('%d-%m-%Y')

# Plot cocktail sales

plt.figure(figsize=(20,20))
plot = sns.catplot(x='Datum', y='Count', col='Omschrijving', data=cocktail_counts, hue='Category', kind='point',
                   sharex=False, col_wrap=3, ci=None)
plot.set_xticklabels(rotation=90)
plot.set_titles(size=15)
plt.yticks([0, 1, 2, 3])
plot.fig.suptitle('Verkoop van cocktails\n\n', size=30)
plot.tight_layout()
#plot.savefig('/home/tom/Projects/Coffee/plots/cocktail_sales.png')









