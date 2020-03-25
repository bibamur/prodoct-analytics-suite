# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 05:50:15 2019

@author: bibam
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib 
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta



all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')
all_user_events_df['date'] = all_user_events_df['date'].astype(str).str[:-6] # remove timestamp
all_user_events_df['date'] = pd.to_datetime(all_user_events_df['date'])
all_user_events_df.set_index('date', inplace = True)

"""get time periods"""
time_periods_df = pd.read_csv('..\\data\\time_periods_df.csv', index_col = 0)







            

"""event_counts_by_date_df = pd.DataFrame()    """

def caculate_event_counts_by_period(events_in_question):
    events_counts_by_period_df = pd.DataFrame()
    for index, period in time_periods_df.iterrows():
        period_start_date = period['start_date']
        period_end_date = period['end_date']        
        all_period_events_df = all_user_events_df.loc[period_start_date:period_end_date]
        for event_id, event in events_in_question.items():
            period_event_df = all_period_events_df.loc[
                    (all_period_events_df[list(event)] == pd.Series(event)).all(axis = 1)
                    ]
            
            period_event_counts_dict = {
                    'event_id':[event_id],
                    'period': [period['time_period_id']],
                    'Total':[len(period_event_df)],
                    'Unique users':[len(period_event_df['user_id'].unique())]
            }
            events_counts_by_period_df = events_counts_by_period_df.append(pd.DataFrame(period_event_counts_dict))
    return events_counts_by_period_df


def plot_event_counts(events_counts_by_period_df, total_or_unique): 
    fig = plt.figure()
    ax = plt.axes()
    for event_id in events_counts_by_period_df['event_id'].unique():
        event_counts_df = events_counts_by_period_df.loc[events_counts_by_period_df['event_id']==event_id]
        #ax.xaxis_date()
        ax.plot(event_counts_df['period'].values, event_counts_df[total_or_unique].values, marker = 'o', label = event_id)
        
    
        
        
        for i,j in zip(event_counts_df['period'].values, event_counts_df[total_or_unique].values):
            ax.annotate(j,(i,j))
        #plt.xticks(event_counts_df['count'].values)
    plt.xticks(events_counts_by_period_df['period'].unique())
    fig.autofmt_xdate()
    plt.legend(loc="upper right")
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
            
events_counts_by_period_df = caculate_event_counts_by_period(events_in_question)
plot_event_counts(events_counts_by_period_df, 'Unique users')
plot_event_counts(events_counts_by_period_df, 'Total')
#