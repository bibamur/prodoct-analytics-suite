# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import json

# Load metadata
with open('..\\data\\events_metadata.json', 'r') as f:
    events_metadata = json.load(f)

with open('..\\data\\periods_metadata.json', 'r') as f:
    periods_metadata = json.load(f)


# Set string constants from events metadata
events_data_path = events_metadata['events_data_path']
timestamp_column = events_metadata['timestamp_column']
user_id_column = events_metadata['user_id_column']

# Set string constants from events metadata
periods_data_path = periods_metadata['periods_data_path']
start = periods_metadata['period_start']
end = periods_metadata['period_end']
period_id_str = periods_metadata['period_id']

# Set string constants needed to parse the event_counts_config.json
event_counts_config_path = '..\\event_counts\\event_counts_config.json'
events_str = 'events'
event_name_str = 'name'
event_conditions_str = 'conditions'

# Set string constant to use in the script
counts_str = 'counts'


# Data preparation
all_events_df = pd.read_csv(events_data_path)  # Load events data
all_events_df[timestamp_column] = all_events_df[timestamp_column].astype(str).str[:-6]  # Remove timestamp from the date
all_events_df[timestamp_column] = pd.to_datetime(all_events_df[timestamp_column])  # Change date type to datetime
all_events_df.set_index(timestamp_column, inplace=True)  # Set date as index

time_periods_df = pd.read_csv(periods_data_path, index_col=0)


def counts_by_period(events: [{}]) -> (pd.DataFrame, pd.DataFrame):
    """
    Gets list of events as input. Each event is described by:
        name - event name
        conditions - dict of conditions to apply to all_user_events_df to get this event.
    Returns 2 DataFrames:
        total_counts_df - total count of events per event per period
        unique_counts_df - count of unique users that performed particular event per period
    """

    unique_counts_df = pd.DataFrame()
    total_counts_df = pd.DataFrame()
    for index, period in time_periods_df.iterrows():
        period_id = period[period_id_str]
        all_period_events_df = all_events_df.loc[period[start]:period[end]]
        event_names = []
        event_totals = []
        event_uniques = []
        for event in events:
            conditions = event[event_conditions_str]
            period_events_df = all_period_events_df.loc[
                (all_period_events_df[list(conditions)] == pd.Series(conditions)).all(axis=1)
            ]
            event_names.append(event[event_name_str])
            event_totals.append(len(period_events_df))
            event_uniques.append(len(period_events_df[user_id_column].unique()))

        total_counts_dict = {
            period_id_str: [period_id] * len(events),
            event_name_str: event_names,
            counts_str: event_totals
        }
        total_counts_df = total_counts_df.append(pd.DataFrame(total_counts_dict))

        unique_counts_dict = {
            period_id_str: [period_id] * len(events),
            event_name_str: event_names,
            counts_str: event_uniques
        }
        unique_counts_df = unique_counts_df.append(pd.DataFrame(unique_counts_dict))

    return total_counts_df, unique_counts_df


def plot_event_counts(counts_df: pd.DataFrame, ax: plt.Axes, title: str):
    """Gets DataFrame with counts, subplot and title, plots event_counts graph on the given subplot"""
    event_counts_df = pd.DataFrame()
    for event_id in [event[event_name_str] for event in events_to_plot]:
        event_counts_df = counts_df.loc[counts_df[event_name_str] == event_id]
        ax.plot(event_counts_df[period_id_str].values, event_counts_df[counts_str].values, marker='o', label=event_id)

        for period, counts in zip(event_counts_df[period_id_str].values, event_counts_df[counts_str].values):
            ax.annotate(counts, (period, counts))  # annotates plot with value near each data point

    ax.set_xticks(event_counts_df[period_id_str].unique())
    ax.set_ylabel(title)
    ax.set_title(title)


with open(event_counts_config_path, 'r') as f:
    events_to_plot = json.load(f)[events_str]


total_df, unique_df = counts_by_period(events_to_plot)


plt.rcParams.update({'font.size': 22})
fig, axs = plt.subplots(2)
plot_event_counts(total_df, axs[0], 'Total number of events.')
plot_event_counts(unique_df, axs[1], 'Total number of unique users.')
plt.show()
