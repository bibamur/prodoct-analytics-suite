# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 09:59:25 2019

@author: bibam
"""

import pandas as pd
import numpy as np
import datetime
import matplotlib 
import matplotlib.pyplot as plt

"""
Calculate_funnel_event_counts function takes following inputs:
1. Dataframe with funnel
2. time period start/end dates
3. Dataframe with user events

Actions sequence:
1. Get all events that are equal to first event in funnel. 
2. Get all users having first funnel event in period
- if no users found - skip time period
3. If users found, filter out all events that are before the start date of the period 
4. Put the list of events for each user into user_event_dict = {'user_id_1':[list of all events that belong to funnel for user_id_1] ...}
5. Get list of events from funnel dataframe - funnel_in_question_events_list
6. Use function get_all_events_in_funnel with arguments user_event_dict and funnel_in_question_events_list to get the calculated funnel for the specific period.
7. Repeat for the next time period, return event_counts_by_time_period = {'time_period_id':{'funnel_event_1': count1, 'funnel_event_2': count2, ...}}

"""

def calculate_funnel_event_counts(funnel_in_question, time_period_start_date, time_period_end_date, events_df): # events_df = all_user_events_in_funnel
    """put all events in funnel into list"""
    funnel_in_question_events_list = [tuple(x) for x in funnel_in_question[user_event_keys].values]
    
    """get all first funnel events using multiindex"""
    i3 = events_df.set_index(user_event_keys).index
    i4 = funnel_in_question.loc[funnel_in_question['order']==1].set_index(user_event_keys).index    
    first_funnel_events_in_user_events = events_df[i3.isin(i4)]
    
    """get all users with first event during the period"""
    all_users_with_first_funnel_event_in_time_period = first_funnel_events_in_user_events.loc[
                (first_funnel_events_in_user_events[time_stamp_key] >= time_period_start_date)
                & (first_funnel_events_in_user_events[time_stamp_key] < time_period_end_date), user_id_key].unique()
    funnel_event_counts = {}        
    if all_users_with_first_funnel_event_in_time_period.size == 0: return funnel_event_counts
    
    """fiter out all events after period start date, set index to user_id to increase speed of further processing"""
    events_in_funnel_df = events_df.loc[
                (events_df[time_stamp_key]>= time_period_start_date)
                #& (events_df[time_stamp_key] < time_period_end_date)
                ]
    events_in_funnel_df.set_index('user_id', inplace=True)    

    
    user_funnel_events = []
    all_users_funnel_events = []
 
    for user in all_users_with_first_funnel_event_in_time_period:
        """get events for particular user, sort by timestamp and represent as a list"""
        user_funnel_events = events_in_funnel_df.loc[[user]][user_event_keys_and_timestamp_key]
        user_funnel_events.sort_values(time_stamp_key, inplace = True)
        user_funnel_events = [tuple(x) for x in user_funnel_events[user_event_keys].values]

        """apply funnel to the list of events for particular user (see next function)"""   
        user_funnel_events = apply_funnel_to_set_of_events(user_funnel_events, funnel_in_question_events_list)
        
        
        """store all funnel events in one big list to build a funnel"""
        all_users_funnel_events.extend(user_funnel_events)
        #print ("time 11: {}".format(datetime.datetime.now()))     
    """calculate counts of each event to build a funnel, store counts into funnel_event_counst list and return it"""    
    for event in funnel_in_question_events_list:
        funnel_event_counts[event] = all_users_funnel_events.count(event)
        #event_counts_by_time_period[time_period] = funnel_event_counts
   
    return funnel_event_counts
    


"""
apply_funnel_to_set_of_events(...) returns part of the funnel that was accomplished by user.
it takes funnel_events and user_events as inputs. Each of these two variables is a lists of events:
    - funel_events - list of events in funnel
    - user_events - list of events for particular user
1. Function searches for the first (next) element from the user_events which is equal to the current funnel event (from funnel_events starting from the first).
2. If there's an event in user_events that is equal to current funnel event then:
    a. User accomplished current step in funnel, so, event is appended to the events_in_funnel list (represents part of the funnel accomplished by user) 
    b. Then all events that were completed before the current one are dropped from user_events.
    c. Then function goes to the step 1 with the next event from funnel. If current funnel event is last, events_in_funnel is returned.
3. If there's no event in user_events that is equal to current funnel event, then user didn't accomplished this step of the funnel, so function returns events_in_funnel.

As a result, events_in_funnel is part of the funnel which was accomplished by particular user.

"""
def apply_funnel_to_set_of_events(funnel_events, user_events):
    events_in_funnel = []
    for funnel_event in funnel_events:
        event_index= next((event_index for (event_index,user_event) in enumerate(user_events) if (user_event == funnel_event)),None)
        
        if event_index is None: return events_in_funnel
        else:
            events_in_funnel.append(user_events[event_index])
            if len(user_events)>event_index+1:
                user_events = user_events[event_index+1:]
            else: break    
    return events_in_funnel





""" define necessary columns"""
user_id_key = 'user_id'
user_event_keys = ['task_id','action_type']
time_stamp_key = 'date'
user_event_keys_and_timestamp_key = user_event_keys + [time_stamp_key]
funnel_mandatory_columns_keys = ['funnel_id','order']
event_name_index = user_event_keys.index('task_id')
label_key = 'label'
funnel_id_key = 'funnel_id'

"""get funnels"""
funnels_in_question = pd.read_csv('funnels_in_question.csv')
labels = funnels_in_question[[funnel_id_key, label_key]]
labels.set_index(funnel_id_key, inplace = True)
funnels_in_question = funnels_in_question[funnel_mandatory_columns_keys+user_event_keys].reset_index(drop = True)

"""get time period"""
start_date = '2017-08-24'
end_date = '2020-01-06'


"""get events"""
all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')

funnels_dict = {}
for funnel_id in  funnels_in_question[funnel_id_key].unique():
    funnel_in_question = funnels_in_question.loc[funnels_in_question['funnel_id'] == funnel_id]
    
    """filter out all events that are not in the funnel"""
    i1 = all_user_events_df.set_index(user_event_keys).index
    i2 = funnel_in_question.set_index(user_event_keys).index
    all_user_events_in_funnel_df = all_user_events_df[i1.isin(i2)]
    
    """add funnel into dictionary"""
    funnels_dict[funnel_id] = calculate_funnel_event_counts(funnel_in_question,start_date, end_date, all_user_events_in_funnel_df)
    



"""Plot funnels"""
fig, axs = plt.subplots(len(funnels_dict))

for ax, funnel_id in zip(axs, funnels_dict.keys()):
    funnel_event_names = [str(item[event_name_index]) for item in funnels_dict[funnel_id]]
    y = list(reversed(labels.loc[funnel_id][label_key].tolist()))
    w = list(reversed(list(funnels_dict[funnel_id].values())))
    ax.barh(y = y, width = w, color='blue')
    ax.set_title(funnel_id, size=35)
    for i, v in enumerate(w):
       ax.text(v + 3, i-0.25, str(v), color='blue', fontweight='bold')
    ax.grid(axis='x', alpha=0.75)
    ax.tick_params(axis="x", labelsize=25)
    ax.tick_params(axis="y", labelsize=22)


    
plt.show()