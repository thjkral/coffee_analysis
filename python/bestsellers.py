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

import dataPrep


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
plt.show()
plt.close()

# Do data preperations before analysis
df_w = dataPrep.prep(df_w)

# Plot missing values after cleaning
plt.figure(figsize=(10, 15))
sns.heatmap(df_w.isna(), cmap='viridis', yticklabels=False, cbar=False)
plt.title('Missing values after dropping columns', size=20)
plt.show()
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

