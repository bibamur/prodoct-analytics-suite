# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Any, Dict

import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from user_events import UserEvents
import user_events as uev
from event_type import EventType
import event_type as et


@dataclass(frozen=True)
class FunnelEventTypes:
    funnel_event_types: List[EventType]
    start_date: str
    end_date: str
    funnel_name: str


def init_funnel_event_types_from_config(config_path: str) -> FunnelEventTypes:
    """
    Args:
        config_path - path to funnels config
    Returns:
          object of FunnelEventTypes containing the list of EventType in funnel and metadata attributes
    """

    with open(os.path.abspath(config_path), 'r') as f:
        funnels_config = json.load(f)
    funnel_name = funnels_config['funnel_id']
    start_date = funnels_config['start_date']
    end_date = funnels_config['end_date']
    config_funnel_events = funnels_config['funnel_events']
    funnel_event_types = []
    for event_type in config_funnel_events:
        funnel_event_types.append(EventType(event_type['name'], event_type['conditions']))

    return FunnelEventTypes(funnel_event_types, start_date, end_date, funnel_name)


def users_with_first_event(first_event: EventType, start: str, end: str, user_events: UserEvents) -> List:
    """
    Args:
        - funnel_event - first EventType from funnel
        - user_events - UserEvent class instance with data
        - start/end dates of the period

    Returns:
        - List of unique user_id who have first event within the period.
    """

    timestamp_column = user_events.timestamp_column
    user_id_column = user_events.user_id_column

    # Get all first funnel events in events_df
    user_events.filter_by_event_type(first_event)
    first_events = user_events.data

    # If no first events found - return empty dict
    users = []
    if len(first_events) == 0:
        return users

    # Get all users with first event during the period
    users = first_events.loc[
        # (first_events[timestamp_column] >= start) &  # this condition not needed as events_df already filtered
        (first_events[timestamp_column] < end), user_id_column].unique()

    return users


def funnel_event_counts(funnel_event_types: List[EventType], users: List, user_events: UserEvents) -> {}:
    """
    Args:
        funnel_event_types: ordered list of all EventType instances from funnel
        users: all users we need to calculate funnel for
        user_events: UserEvents class instance with the data

    """
    timestamp_column = user_events.timestamp_column
    data = user_events.data

    all_users_funnel_events = {}
    for user in users:
        # Get events for particular user, sort by timestamp
        user_df = data.loc[[user]]
        user_df.sort_values(timestamp_column, inplace=True)

        # For particular user get list of all her funnel events up to the last reached
        user_funnel = user_funnel_events(user_df, funnel_event_types)

        # Store all user funnel events in one big list to build a funnel
        for event_type_name in user_funnel:
            if event_type_name in all_users_funnel_events:
                all_users_funnel_events[event_type_name] += 1
            else:
                all_users_funnel_events[event_type_name] = 1

    return all_users_funnel_events


def user_funnel_events(user_df: pd.DataFrame, funnel: List[EventType]) -> []:
    """
    Gets:
        - user_df - DataFrame with all events for particular user in chronological order
        - funnel - list of events from funnels_config.json

    Returns list of all user's funnel events up to the last reached.
    """

    event_type_str = et.StringConstants.event_type.value
    events_in_funnel = []
    user_df.reset_index(inplace=True, drop=True)
    for funnel_event in funnel:
        funnel_df = user_df.loc[user_df[event_type_str] == funnel_event.name]
        if len(funnel_df) > 0:
            event_index = funnel_df.index[0]
        else:
            return events_in_funnel
        user_df = user_df.loc[event_index + 1:]
        events_in_funnel.append(funnel_event.name)

    return events_in_funnel


def plot_funnel(ax: plt.Axes, event_counts: Dict, title: str):
    y = list(reversed(list(event_counts.keys())))
    w = list(reversed(list(event_counts.values())))
    ax.barh(y=y, width=w, color='blue')
    plt.rcParams.update({'font.size': 22})
    for i, v in enumerate(w):
        ax.text(v + 3, i - 0.25, str(v), color='blue', fontweight='bold')

    ax.grid(axis='x', alpha=0.75)
    ax.tick_params(axis="x", labelsize=25)
    ax.tick_params(axis="y", labelsize=22)
    ax.set_title(title)


if __name__ == '__main__':
    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')

    funnel = init_funnel_event_types_from_config('../funnels/funnels_config.json')

    # Filter out all events before period start date, set index to user_id to increase speed of further processing
    events.data = events.data.loc[
        (events.data[events.timestamp_column] >= funnel.start_date)  # If all events after period start are needed
        # & (events.data[events.timestamp_column] < funnel.start_date)   # If only events within period are needed
    ]
    events.data.set_index(events.user_id_column, inplace=True, drop=False)

    # Filter by funnel Event Types
    events.filter_by_event_type(funnel.funnel_event_types, add_event_type_name=True)

    users_in_question = users_with_first_event(funnel.funnel_event_types, funnel.start_date, funnel.end_date, events)
    event_counts = funnel_event_counts(funnel.funnel_event_types, users_in_question, events)

    fig, ax = plt.subplots()
    plot_funnel(ax, event_counts, funnel.funnel_name)

    plt.show()
