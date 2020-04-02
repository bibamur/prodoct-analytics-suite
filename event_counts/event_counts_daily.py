# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 15:49:50 2019

@author: bibam
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib 
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta




all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')
all_user_events_df['date'] = all_user_events_df['date'].astype(str).str[:-6]
all_user_events_df['date'] = pd.to_datetime(all_user_events_df['date'])
all_user_events_df.set_index('date', inplace = True)




def calculate_total_events_and_unique_users(period_start_date, period_end_date, events_in_question):
    event_counts_by_date_df = pd.DataFrame()    
    events_df = all_user_events_df.loc[period_start_date:period_end_date]
    for event_id, event in events_in_question.items():
        event_df = events_df.loc[(events_df[list(event)] == pd.Series(event)).all(axis = 1)]
        delta = datetime.strptime(period_end_date, '%Y-%m-%d') - datetime.strptime(period_start_date, '%Y-%m-%d')
        for i in range(delta.days):
                day = datetime.strptime(period_start_date, '%Y-%m-%d') + timedelta(days=i)
                day_events = event_df.loc[str(day.date())]
                day_counts_dict = {
                'event_id':[event_id],
                'date': [day.date()],
                'Total':[len(day_events)],
                'Unique users':[len(day_events['user_id'].unique())]
                }
                event_counts_by_date_df = event_counts_by_date_df.append(pd.DataFrame(day_counts_dict)) 
    return event_counts_by_date_df
            
def plot_event_counts(event_counts_by_date_df, total_or_unique): 
    fig = plt.figure()
    ax = plt.axes()
    
    
    for event_id in event_counts_by_date_df['event_id'].unique():
        event_counts_df = event_counts_by_date_df.loc[event_counts_by_date_df['event_id']==event_id]
        ax.xaxis_date()
        ax.plot(event_counts_df['date'].values, event_counts_df[total_or_unique].values, marker = 'o', label = event_id)
        
    
        
        
        for i,j in zip(event_counts_df['date'].values, event_counts_df[total_or_unique].values):
            ax.annotate(j,(i,j), fontsize=15)

    plt.xticks(event_counts_by_date_df['date'].unique())
    fig.autofmt_xdate()
    plt.legend(loc="upper right", fontsize=15)
    
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Number of events: ' + total_or_unique, fontsize=15)
    plt.title('Number of events: ' + total_or_unique, fontsize=15)
    plt.show()



events_in_question = {
        'Task Started':
            {
            'action_type':'started'
            },
        'Task Ended':
            {
            'action_type':'done'            
            },
        'Task Skipped':
            {
            'action_type':'skipped'            
            }
            }


period_start_date = '2019-09-16'
period_end_date = '2019-10-14'




event_counts_by_date_df = calculate_total_events_and_unique_users(period_start_date, period_end_date, events_in_question )
plot_event_counts(event_counts_by_date_df, 'Total') 
plot_event_counts(event_counts_by_date_df, 'Unique users')
#