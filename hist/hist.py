# -*- coding: utf-8 -*-
from typing import List, Dict, Set

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.lines as mlines
from user_events import UserEvents
import user_events as uev
import json
import os
from event_type import EventType
import event_type as et

# Set string constant to use in the script
event_type_str = et.StringConstants.event_type.value


def calculate_histograms(events: UserEvents, event_types: List[EventType], all_users: Set[str]) -> Dict[str, pd.Series]:
    """
    Args:
        events - UserEvents instance with user events data
        event_types - list of event types we need to calculate histogram for from hist config.
        all_users - set with all users (even those that have no events). Needed to calculate users with zero events
    Returns:
        hist_dict - dictionary with key = event type name, value = Series with user event counts
    """
    hist_dict = {}
    for event_type in event_types:
        name = event_type.name
        event_type_data = events.data.loc[events.data[event_type_str] == name, events.user_id_column]
        counts = event_type_data.value_counts()

        event_type_users = set(event_type_data.unique())
        zero_users = pd.Series(0, index=all_users.difference(event_type_users))
        counts = pd.concat([counts, zero_users])

        hist_dict[name] = counts

    return hist_dict


def plot_histogram(all_user_event_counts, title, x_label, y_label):
    hist, bins = np.histogram(list(all_user_event_counts), bins=(all_user_event_counts.max()))

    plt.figure(figsize=[10,8])
    plt.bar(bins[:-1], hist, width = 0.5, color='#0504aa', alpha=0.7)
    plt.xlim(min(bins), max(bins))
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel(x_label,fontsize=35)
    plt.xticks(np.arange(0, bins.max(), 5), fontsize=25)
    
    plt.yticks(fontsize=25)
    plt.ylabel(y_label, fontsize=25)
    plt.title(title, fontsize=25)


if __name__ == '__main__':
    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')
    events.add_period_to_data()

    # filter data by start/end dates and event types in question
    config_path = '../hist/hist_config.json'
    with open(os.path.abspath(config_path), 'r') as f:
        config = json.load(f)

    config_events = config['events']
    period_start_date = config['start_date']
    period_end_date = config['end_date']
    events.data = events.data.loc[period_start_date:period_end_date]

    event_types = et.load_event_types_from_json(config_events)
    events.filter_by_event_type(event_types, add_event_type_name=True)

    all_users = set(events.data[events.user_id_column].unique())
    hists = calculate_histograms(events, event_types, all_users)
    for hist_name, hist in hists.items():
        plot_histogram(hist, hist_name, 'Number of events', 'Frequency')

    plt.show()

