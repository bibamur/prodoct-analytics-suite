# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 05:59:50 2019

@author: bibam
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

#time_period_in_question = 22

all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')
all_user_events_df['date'] = all_user_events_df['date'].astype(str).str[:-6] # remove timestamp
all_user_events_df['date'] = pd.to_datetime(all_user_events_df['date'])
all_user_events_df.set_index('date', inplace = True)

"""get time periods"""
time_periods_df = pd.read_csv('..\\data\\time_periods_df.csv', index_col = 0)
#time_periods_df = time_periods_df[25:]


all_users = all_user_events_df['user_id'].unique()


users_by_period_dict = {}
for index, row in time_periods_df.iterrows():
    end_date = datetime.strptime(row.end_date, '%Y-%m-%d') - timedelta(days=1)
    end_date = str(end_date)[:10]
    users = all_user_events_df[row.start_date:end_date]['user_id'].unique()
    users_by_period_dict[row.time_period_id] = users
    


periods_by_user_dict = {}
for period, users in users_by_period_dict.items():
    for user in users:
        if user not in periods_by_user_dict.keys():  periods_by_user_dict[user] = np.asarray([period])
        else: periods_by_user_dict[user] = np.append(periods_by_user_dict[user], period)

retention_dict = {}

retention_list = np.array([])

for user in periods_by_user_dict.keys():
    retention_list = np.append(retention_list, periods_by_user_dict[user] - periods_by_user_dict[user][0])



unique, counts = np.unique(retention_list, return_counts=True)


retention_graph = pd.DataFrame(
        {'Retention Period': unique,
         'Number of users':counts,
         'Ret %': counts/counts.max()
         })


retention_graph=retention_graph.sort_index().copy()

print(retention_graph)


retention_graph.plot(kind = 'line',x='Retention Period', y ='Ret %', figsize=(15,10), marker = 'o')
plt.title('Retention by time period', fontsize = 35)

plt.rcParams.update({'font.size': 25})
plt.ylim([0, 1])
plt.xlim([0, retention_graph['Retention Period'].max()])
plt.xticks(np.arange(0, retention_graph['Retention Period'].max()+1), fontsize=20)
plt.yticks(fontsize=20)
plt.grid()


for index,row in retention_graph.iterrows():
    plt.text(row['Retention Period'], row['Ret %'], round(row['Ret %']*100,2), fontsize=25)

plt.show()


#