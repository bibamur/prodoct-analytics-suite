# -*- coding: utf-8 -*-
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from user_events import UserEvents
import user_events as uev
from event_type import EventType
import event_type as et


# Set string constant to use in the script
event_type_str = et.StringConstants.event_type.value


def counts_by_period(user_events: UserEvents, types: List[EventType]) -> pd.DataFrame:
    """
    Calculates total number of events by event type by period
    Args:
        User Events instance
        list of event types
    Returns:
         DataFrame with total event counts
    """
    data = user_events.data
    period_id = user_events.period_id_column
    user_id = user_events.user_id_column
    tasks_counts = data.groupby([period_id, event_type_str])[user_id].agg('count')
    tasks_counts = tasks_counts.reset_index()
    return tasks_counts


def uniques_by_period(user_events: UserEvents, types: List[EventType]) -> (pd.DataFrame):
    """
    Calculates number of unique users who performed the event by event type by period
    Args:
        User Events instance
        list of event types
    Returns:
         DataFrame with unique users counts
    """
    data = user_events.data
    period_id = user_events.period_id_column
    user_id = user_events.user_id_column
    unique_counts = data[[period_id, event_type_str, user_id]].drop_duplicates()
    unique_counts = unique_counts.groupby([period_id, event_type_str])[user_id].agg('count')
    unique_counts = unique_counts.reset_index()
    return unique_counts


def plot_event_counts(counts_df: pd.DataFrame, event_types: List[EventType], ax: plt.Axes, period_id: str,
                      user_id: str, title: str):
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
        x_coord = event_counts_df[period_id].values
        y_coord = event_counts_df[user_id].values
        ax.plot(x_coord, y_coord,
                marker='o', label=event_type.name)

        for x, y in zip(x_coord, y_coord):
            ax.annotate(y, (x, y))  # annotates plot with value near each data point

    ax.set_xticks(x_coord)
    ax.set_ylabel(title)
    ax.set_title(title)
    ax.legend()


if __name__ == '__main__':
    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')
    events.add_period_to_data()

    config_path = '../event_counts/event_counts_config.json'
    with open(os.path.abspath(config_path), 'r') as f:
        config_events = json.load(f)['events']

    event_types = et.load_event_types_from_json(config_events)
    events.filter_by_event_type(event_types, add_event_type_name=True)

    total_df = counts_by_period(events, event_types)
    unique_df = uniques_by_period(events, event_types)

    plt.rcParams.update({'font.size': 22})
    fig, axs = plt.subplots(2)
    plot_event_counts(total_df, event_types, axs[0], events.period_id_column, events.user_id_column,
                      'Total number of events.')
    plot_event_counts(unique_df, event_types, axs[1], events.period_id_column, events.user_id_column,
                      'Total number of unique users.')
    plt.show()
