#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 11:18:08 2022

@author: tom
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime


start_time  = datetime.datetime.now()

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

# Calculate the percentage of products without categories
miss_val_perc = round((df_i['Category'].isna().sum() * 100) / df_i['Category'].shape[0], 2)
print(f'Percentage of products without category: {miss_val_perc}')

# Make names the index to add categories later
df_i.set_index('Name', inplace=True)



'''
Calculate best selling products and plot
'''


# Enter a subset for dates (year-month-day)
df_w = df_w[(df_w['Datum'] >= '2020-01-01') & (df_w['Datum'] <= '2020-03-31')]


# Count the sales of the different items
item_counts = df_w.explode('Omschrijving').reset_index().groupby('Omschrijving').Omschrijving.count()
item_counts = item_counts.to_frame()
item_counts.rename(columns={'Omschrijving':'Count'}, inplace=True)
item_counts['new_col'] = np.arange(1, item_counts.shape[0] + 1)
item_counts = item_counts.reset_index().set_index('new_col')




def get_category(product): # Add categories to products
    try:
        return df_i.loc[product, 'Category']
    except KeyError:
        return 'no_category'
    except pd.IndexingError:
        return 'unique_item'

item_counts['Category'] = item_counts['Omschrijving'].apply(lambda x: get_category(x))
item_counts['Category'] = item_counts['Category'].fillna(value='no_category')

# Check if there are products in multiple categories
df_zi = df_i.reset_index()
if df_zi[df_zi.duplicated(['Name'])].shape[0] >= 1:
    print('WARNING: duplicate products/categories')
else:
    print('Data is duplicate free')
    
del df_zi




# Best selling products overall:
#print(item_counts.sort_values('Count', ascending=False, ignore_index=True).head(5))


item_counts


# Calculate best selling products per category
df_bestsellers = item_counts.sort_values(['Category', 'Count'], ascending=[True, False]).groupby('Category').head(10)
df_one_occ = df_bestsellers['Category'].value_counts() > 1
df_bestsellers = df_bestsellers[df_bestsellers['Category'].isin(df_one_occ[df_one_occ].index)]

# Plot the bestsellers
cat_plot = sns.catplot(x='Omschrijving', y='Count', data=df_bestsellers, col='Category', kind='bar', 
            sharex=False, sharey=False, col_wrap=3,
            palette=sns.color_palette('Spectral'))
cat_plot.set_xticklabels(rotation=90)
cat_plot.fig.suptitle('Sales per categorie | Kwartaal 1, 2020\n\n', size=30)
cat_plot.set_titles(size=15)
cat_plot.set_xlabels('Product')
cat_plot.set_ylabels('Aantallen')
cat_plot.tight_layout()
cat_plot.savefig('/home/tom/Projects/Coffee/plots/2020/sales_Q1_2020.png')







stop_time = datetime.datetime.now()
run_time = stop_time - start_time
print(f'\n\n\n############\nRuntime: {run_time.seconds} seconds and {run_time.microseconds} microseconds')

