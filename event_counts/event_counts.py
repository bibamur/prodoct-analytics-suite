# -*- coding: utf-8 -*-
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import json
from dataclasses import dataclass
import os


@dataclass
class EventType:
    name: str
    conditions: Dict


# Load metadata
data_path = '../data'
events_metadata_filename = 'events_metadata.json'
periods_metadata_filename = 'periods_metadata.json'

with open(os.path.join(data_path, events_metadata_filename), 'r') as f:
    events_metadata = json.load(f)

with open(os.path.join(data_path, periods_metadata_filename), 'r') as f:
    periods_metadata = json.load(f)

# Set string constants from events metadata
events_data_path = events_metadata['events_data_path']
timestamp_column = events_metadata['timestamp_column']
user_id_column = events_metadata['user_id_column']

# Set string constants from periods metadata
periods_data_path = periods_metadata['periods_data_path']
start = periods_metadata['period_start']
end = periods_metadata['period_end']
period_id_str = periods_metadata['period_id']

# Prepare data
events_data = pd.read_csv(events_data_path)  # Load events data
events_data[timestamp_column] = events_data[timestamp_column].astype(str).str[:-6]  # Remove timestamp from the date
events_data[timestamp_column] = pd.to_datetime(events_data[timestamp_column])  # Change date type to datetime
events_data.set_index(timestamp_column, inplace=True)  # Set date as index

time_periods = pd.read_csv(periods_data_path, index_col=0)
events_data[period_id_str] = 0

# Set string constant to use in the script
event_type_str = 'event_type'


for index, period in time_periods.iterrows():
    period_id = period[period_id_str]
    events_data.loc[period[start]:period[end], period_id_str] = period_id

# Prepare event types
config_path = '../event_counts'
config_filename = 'event_counts_config.json'
with open(os.path.join(config_path, config_filename), 'r') as f:
    config_events = json.load(f)['events']
event_types = []
for config_event in config_events:
    event_types.append(EventType(config_event['name'], config_event['conditions']))


# Filter data by event types
def filter_by_event_type(data: pd.DataFrame, types: List[EventType]):
    data_filter = pd.Series(False, index=data.index)
    data[event_type_str] = ''
    for event_type in types:
        columns = list(event_type.conditions.keys())
        conditions = pd.Series(event_type.conditions)
        event_filter = (data[columns] == conditions).all(axis=1)
        data.loc[event_filter, event_type_str] = event_type.name  # add event name to DataFrame
        data_filter |= event_filter
    return data[data_filter]


events_data = filter_by_event_type(events_data, event_types)


def counts_by_period(data: pd.DataFrame, types: List[EventType]) -> (pd.DataFrame):
    """
    Calculates total number of events by event type by period
    Args:
        User data
        list of event types
    Returns:
         DataFrame with total event counts
    """
    tasks_counts = data.groupby([period_id_str, event_type_str])[user_id_column].agg('count')
    tasks_counts = tasks_counts.reset_index()
    return tasks_counts


def uniques_by_period(data: pd.DataFrame, types: List[EventType]) -> (pd.DataFrame):
    """
    Calculates number of unique users who performed the event by event type by period
    Args:
        User data
        list of event types
    Returns:
         DataFrame with unique users counts
    """
    unique_counts = data[[period_id_str, event_type_str, user_id_column]].drop_duplicates()
    unique_counts = unique_counts.groupby([period_id_str, event_type_str])[user_id_column].agg('count')
    unique_counts = unique_counts.reset_index()
    return unique_counts


def plot_event_counts(counts_df: pd.DataFrame, ax: plt.Axes, title: str):
    """
    Plots event_counts graph on the given subplot
    Args:
        DataFrame with counts
        Subplot to draw the plot on
        Title of the plot
    """
    event_counts_df = pd.DataFrame()
    for event_type in event_types:
        event_counts_df = counts_df.loc[counts_df[event_type_str] == event_type.name]
        x_coord = event_counts_df[period_id_str].values
        y_coord = event_counts_df[user_id_column].values
        ax.plot(x_coord, y_coord,
                marker='o', label=event_type.name)

        for x, y in zip(x_coord, y_coord):
            ax.annotate(y, (x, y))  # annotates plot with value near each data point

    ax.set_xticks(x_coord)
    ax.set_ylabel(title)
    ax.set_title(title)
    ax.legend()


total_df = counts_by_period(events_data, event_types)
unique_df = uniques_by_period(events_data, event_types)

plt.rcParams.update({'font.size': 22})
fig, axs = plt.subplots(2)
plot_event_counts(total_df, axs[0], 'Total number of events.')
plot_event_counts(unique_df, axs[1], 'Total number of unique users.')
#plt.show()
