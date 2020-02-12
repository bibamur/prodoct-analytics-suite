# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 09:53:32 2019

@author: bibam
"""


import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.lines as mlines


"""all_user_events_df"""
all_user_events_df = pd.read_csv('..\\data\\user_events_df.csv')
all_user_events_df['date'] = all_user_events_df['date'].astype(str).str[:-6] # remove timestamp
all_user_events_df['date'] = pd.to_datetime(all_user_events_df['date'])

time_periods_df = pd.read_csv('..\\data\\time_periods_df.csv', index_col = 0)
time_periods_df['start_date'] = pd.to_datetime(time_periods_df['start_date'])
time_periods_df['end_date'] = pd.to_datetime(time_periods_df['end_date'])


first_date_group = all_user_events_df.groupby('user_id')['date'].min()

def get_first_season(time_stamp):
    
    s = time_periods_df.loc[
            (time_periods_df.start_date <= time_stamp)
            & (time_periods_df.end_date > time_stamp),'time_period_id']
    if len(s) == 1: return s.iloc[0]
    else: return -1
    
first_user_season = first_date_group.apply(get_first_season)    

user_time_periods_df = pd.DataFrame({'user_id':first_user_season.index, 'first_time_period_id':first_user_season.values})


all_user_events_df.set_index('date', inplace = True)


"""This function calculates count of events performed by user during his/her first time period"""
def calculate_first_period_user_event_counts(user_events_df):
    all_user_event_counts = pd.Series()
    for time_period_id, start_date, end_date in zip(time_periods_df.time_period_id, time_periods_df.start_date, time_periods_df.end_date):
        #end_date = str((datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(1)).date()) # take previous day
        end_date = end_date - datetime.timedelta(1)
        time_period_events_df = user_events_df.loc[str(start_date):str(end_date)]
        users = user_time_periods_df.loc[user_time_periods_df['first_time_period_id'] == time_period_id,'user_id'].unique() # get all users with first time period equal to the time period in iteration
        #print(users)    
        event_counts = time_period_events_df.loc[time_period_events_df['user_id'].isin(users), 'user_id'].value_counts() # get number of events for each user within period in iteration
        zero_event_users = pd.Series(data = 0, index = [user for user in users if not user in list(event_counts.index)]) # get users with no events within period in iteration
        
       # season_user_event_counts_dict[season_id] = event_counts
        #print(len(all_user_event_counts))
        all_user_event_counts = all_user_event_counts.append(event_counts)
        all_user_event_counts = all_user_event_counts.append(zero_event_users)
    return all_user_event_counts 


def calculate_all_user_event_counts(user_events_df):
    return user_events_df['user_id'].value_counts()



def plot_histogram(all_user_event_counts, title, x_label, y_label):
    hist, bins = np.histogram(list(all_user_event_counts), bins = (all_user_event_counts.max()) )
    #bin_edges
    
    #fig, ax = plt.subplots()
    
    plt.figure(figsize=[10,8])
    
    plt.bar(bins[:-1], hist, width = 0.5, color='#0504aa',alpha=0.7)
    plt.xlim(min(bins), max(bins))
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel(x_label,fontsize=35)
    plt.xticks(np.arange(0,bins.max(),5))
    
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.ylabel(y_label,fontsize=25)
    plt.title(title,fontsize=25)
    plt.show()

def plot_scatter(bivariate_analysis_df, title, x_label, y_label):
    x = bivariate_analysis_df[x_label].values
    y = bivariate_analysis_df[y_label].values
    
    
    plt.figure(figsize=[10,8])
    plt.scatter(x, y,
                c = y, s=(bivariate_analysis_df['Number of occurencies'])*5,  cmap="viridis")
    plt.xlim(x.min(), x.max())
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel(x_label,fontsize=35)
    plt.xticks(np.arange(x.min() -5, x.max(), 5))
    
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.ylabel(y_label,fontsize=25)
    plt.title(title,fontsize=25)
    
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    line = slope*x+intercept
    plt.plot(x, line, 'r')#, label='y={:.2f}x+{:.2f}'.format(slope,intercept))
    red_line = mlines.Line2D([], [], color='red',
                          label='y={:.2f}x+{:.2f},\nr_value = {:.2f},\np_value = {:.2f},\nstd_err ={:.2f}'.format(slope,intercept,r_value,p_value,std_err))
    plt.legend(handles=[red_line], fontsize=25)

    plt.show()



# define events - all social tasks which are done
    
event_1_key = 'Social tasks done'    
event_1 = {
        'is_course': False, #Social task
        'action_type': 'done'
        }
            
user_events_df = all_user_events_df.loc[(all_user_events_df[list(event_1)] == pd.Series(event_1)).all(axis = 1)]

all_user_event_counts_social = calculate_first_period_user_event_counts(user_events_df)
#all_user_event_counts_social = calculate_all_user_event_counts(user_events_df)



plot_histogram(all_user_event_counts_social, 'Number of Users who have completed certain number of Social tasks', 'Number of completed tasks','Frequency')


# define events - all course tasks which are done
event_2_key = 'Course tasks done'    
event_2 = {
        'is_course': True, #Social task
        'action_type': 'done'
        }

user_events_df = all_user_events_df.loc[(all_user_events_df[list(event_2)] == pd.Series(event_2)).all(axis = 1)]

all_user_event_counts_course = calculate_first_period_user_event_counts(user_events_df)
#all_user_event_counts_course = calculate_all_user_event_counts(user_events_df)

all_user_event_counts_course[all_user_event_counts_course>200] = 200 # outliers with more than 200 tasks will be marked as they have 200 tasks (to reduce x-axis) 


plot_histogram(all_user_event_counts_course, 'Number of Users who have completed certain number of Course tasks', 'Number of completed tasks','Frequency')


# Put together DataFrame with all necessary data for bivariate analysis plot
all_user_event_counts_social.name = event_1_key
all_user_event_counts_course.name = event_2_key


bivariate_analysis_df= pd.concat([all_user_event_counts_social, all_user_event_counts_course], axis = 1).fillna(0)
bivariate_analysis_df.sort_index(inplace=True)


num_occurencies = bivariate_analysis_df.groupby(list(bivariate_analysis_df.columns)).size().reset_index()
num_occurencies.columns = [event_1_key,event_2_key,'Number of occurencies']

bivariate_analysis_df = bivariate_analysis_df.merge(num_occurencies, how = 'left', on = [event_1_key,event_2_key])

plot_scatter(bivariate_analysis_df, 'Social vs Course tasks', event_2_key, event_1_key)



    
#all_user_event_counts.hist(bins=120)

""" 
#Calculate cohorts:
cohort_1_not_active = all_user_event_counts_course[all_user_event_counts_course<=4]
cohort_2_active = all_user_event_counts_course[all_user_event_counts_course > 4]

cohort_1_not_active.to_csv('not_active_users_course.csv', header = False)
cohort_2_active.to_csv('active_users_course.csv', header = False)
"""
