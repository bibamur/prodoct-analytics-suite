# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 05:59:50 2019

@author: bibam
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

#time_period_in_question = 22

all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')
all_user_events_df['date'] = all_user_events_df['date'].astype(str).str[:-6] # remove timestamp
all_user_events_df['date'] = pd.to_datetime(all_user_events_df['date'])


start_date = '2019-05-27'
end_date = '2019-06-23'


""" 
users - all users with the very first event during the given time period:
1. group by user_id and get the earliest date
2. get only those users where date is in given time period
"""


users_first_event_date =  all_user_events_df.groupby('user_id')['date'].min()
users_first_event_date =  pd.Series(users_first_event_date.index.values, index = users_first_event_date) #swap index and value in Series
users = users_first_event_date[start_date:end_date].values





#all_user_events_df.set_index('date', inplace = True)

# find fist event by user and compare it with the payment start date




#names =task_action_df['task_name'].unique()

#add season_id to this dataframe - not needed
# take cohort of users who bought the ticket in this season

# calculate retention day for each timestamp by 24h window (using timedelta days)
def calculate_daily_retention(users):
    user_event_dates_dict = {}
    user_retention_days_dict = {}
    for user in users:
        user_event_dates_dict[user] = pd.to_datetime(all_user_events_df.loc[all_user_events_df['user_id']==user,'date'].values)
        if not user_event_dates_dict[user].empty:
            min_timestamp = min(user_event_dates_dict[user])
            dates = user_event_dates_dict[user]
            dates = pd.Series(((dates - min_timestamp).days).drop_duplicates().sort_values())
            user_retention_days_dict[user] = dates
            b = 1
    return user_retention_days_dict

user_retention_days_dict = calculate_daily_retention(users)






# put all retention days into one big Series
all_retention_days = pd.concat(user_retention_days_dict.values())



#prepare dataframe for plotting
daily_retention = pd.DataFrame(
        {'Ret N':all_retention_days.value_counts(),
         'Ret %':all_retention_days.value_counts()/all_retention_days.value_counts().max()
        }
        ).sort_index()

#plot
for index,row in daily_retention.iterrows():
    #print(row['Number of users'])
    if index%7 != 0: continue # show annotation for evety 7th day
    plt.text(index, row['Ret %'], round(row['Ret %']*100,2))


plt.rcParams.update({'font.size': 15})
plt.xticks(daily_retention.index.values)
plt.plot(daily_retention['Ret %'], marker = 'o', color = 'blue')

ax = plt.axes()

ax.xaxis.set_major_locator(plt.MaxNLocator(50))
ax.yaxis.set_major_locator(plt.MaxNLocator(10))

plt.ylim([0, 1])
plt.xlim([0, daily_retention.index.max()])
plt.title('Daily Retention graph', fontsize = 35)
blue_line = mlines.Line2D([], [], color='blue',
                          label='Total users count: ' + str(len(users)) +'\nStart date: ' + str(start_date) + '\nEnd date: '+str(end_date))
plt.legend(handles=[blue_line], fontsize=25)
plt.xlabel('Retention Day N',fontsize=35)
plt.ylabel('Retention %',fontsize=35)

plt.grid()    
plt.show()





#calculate_retention_days(user_event_dates_dict[1009544])

# e.g. user_id | 0,1,5,7,10,30, 35, remove dupes
# merge into one big list, calculate value counts: 0 1000, 1 900, 2 800 ...
# graph daily retention

