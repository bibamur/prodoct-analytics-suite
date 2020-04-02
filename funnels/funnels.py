# -*- coding: utf-8 -*-
from typing import List, Any

import pandas as pd
import matplotlib.pyplot as plt
import json


def funnel_event_counts(funnel: [], start: str, end: str, events_df: pd.DataFrame) -> {}:
    """
    Gets:
        - funnel - list of funnel events from config
        - df - DataFrame with user events to apply funnel to
        - start/end to find all users having first funnel event during this period

    Returns:
        - Dictionary of pairs 'Event name': count, where count is total number of users who reached this funnel event
    """
    # Get all first funnel events in events_df
    first_event = funnel[0]
    cond_keys = list(first_event[event_conditions_str])
    first_event_conditions = pd.Series(first_event[event_conditions_str])
    first_events = events_df[(events_df[cond_keys] == first_event_conditions).all(axis=1)]

    # If no first events found - return empty dict
    counts = {}
    if len(first_events) == 0:
        return counts

    # Get all users with first event during the period
    users = first_events.loc[
        # (first_events[timestamp_column] >= start) &  # this condition not needed as events_df already filtered
        (first_events[timestamp_column] < end), user_id_column].unique()

    events_df.set_index('user_id', inplace=True)
    all_users_funnel_events = []
    for user in users:
        # Get events for particular user, sort by timestamp
        user_df = events_df.loc[[user]]
        user_df.sort_values(timestamp_column, inplace=True)

        # For particular user get list of all her funnel events up to the last reached
        user_funnel = user_funnel_events(user_df, funnel)

        # Store all user funnel events in one big list to build a funnel
        all_users_funnel_events.extend(user_funnel)

    # Calculate counts of each event to build a funnel, store counts into counts list and return it"""
    for event in funnel:
        name = event[event_name_str]
        counts[name] = all_users_funnel_events.count(name)
        # event_counts_by_time_period[time_period] = event_counts

    return counts


def user_funnel_events(user_df: pd.DataFrame, funnel: []) -> []:
    """
    Gets:
        - user_df - DataFrame with all events for particular user in chronological order
        - funnel - list of events from funnels_config.json

    Returns list of all user's funnel events up to the last reached.
    """
    events_in_funnel = []
    for funnel_event in funnel:
        user_df.reset_index(inplace=True, drop=True)
        cond_keys = list(funnel_event[event_conditions_str])
        conditions = pd.Series(funnel_event[event_conditions_str])
        indexes = [event_index for event_index, user_event in user_df[cond_keys].iterrows() 
                               if (user_event == conditions).all()]
        event_index = next(iter(indexes), None)
            
        if event_index is None:
            return events_in_funnel
        else:
            events_in_funnel.append(funnel_event[event_name_str])
            if len(user_df) > event_index + 1:
                user_df = user_df[event_index + 1:]
            else:
                break
    return events_in_funnel


with open('..\\data\\events_metadata.json', 'r') as f:
    events_metadata = json.load(f)

# Setup strings from events metadata
user_id_column = events_metadata['user_id_column']
timestamp_column = events_metadata['timestamp_column']
events_data_path = events_metadata['events_data_path']

# Load events data
all_user_events_df = pd.read_csv(events_data_path)


# Set string constants needed to parse the funnels_config.json
funnels_config_path = '..\\funnels\\funnels_config.json'
funnel_id_str = 'funnel_id'
funnel_events_str = 'funnel_events'
event_name_str = 'name'
event_conditions_str = 'conditions'
order_str = 'order'
funnel_start_date_str = 'start_date'
funnel_end_date_str = 'end_date'

with open(funnels_config_path, 'r') as f:
    funnels_config = json.load(f)

# Get funnels
start_date = funnels_config[funnel_start_date_str]
end_date = funnels_config[funnel_end_date_str]

# Filter out all events before period start date, set index to user_id to increase speed of further processing
all_user_events_df = all_user_events_df.loc[
    (all_user_events_df[timestamp_column] >= start_date)  # If all events after period start are needed
    # & (events_df[time_stamp_key] < time_period_end_date)  # If only events within period are needed
]

funnel_events = funnels_config[funnel_events_str]
# Create filter and filter all_user_events_df by funnel_events
funnel_filter = pd.Series(False, index=all_user_events_df.index)
for event in funnel_events:
    keys = list(event[event_conditions_str])
    funnel_filter |= (all_user_events_df[keys] == pd.Series(event[event_conditions_str])).all(axis=1)
    # TODO move boolean condition to function filter_by_event(events_df, conditions)

filtered_events_df = all_user_events_df[funnel_filter]
filtered_events_df.reset_index(inplace=True, drop=False)

funnels_dict = {}
funnel_id = funnels_config[funnel_id_str]
event_counts = funnel_event_counts(funnel_events, start_date, end_date, filtered_events_df)

# plot funnel
fig, ax = plt.subplots()
y = list(reversed(list(event_counts)))
w = list(reversed(list(event_counts.values())))
ax.barh(y=y, width=w, color='blue')
plt.rcParams.update({'font.size': 22})
for i, v in enumerate(w):
        ax.text(v + 3, i - 0.25, str(v), color='blue', fontweight='bold')

ax.grid(axis='x', alpha=0.75)
ax.tick_params(axis="x", labelsize=25)
ax.tick_params(axis="y", labelsize=22)     
plt.show()