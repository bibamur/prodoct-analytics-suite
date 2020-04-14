# -*- coding: utf-8 -*-
import json
import os
from typing import List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import user_events as uev
from user_events import UserEvents
import event_type as et


def retention_by_period(events: UserEvents):
    """
    Args:
        events - UserEvents instance with user events data and metadata
    Returns:
          retention_list - for each user contains list of periods where user participated. Each period in the list
                           reduced to minimum period
    """
    grouped = events.data.groupby(events.user_id_column)[events.period_id_column].apply(np.array)
    grouped = grouped.dropna()
    grouped = grouped.apply(lambda x: x - np.amin(x))

    retention_list = []
    for periods_list in grouped:
        retention_list.extend(periods_list)
    return retention_list


def plot_retention_by_period(retention_data: List):
    periods_label = 'Retention Period'
    retention_label = 'Retention %'
    users_num_label = 'Number of users'
    unique, counts = np.unique(retention_data, return_counts=True)

    retention_graph = pd.DataFrame(
            {periods_label: unique,
             users_num_label: counts,
             retention_label: counts/counts.max()
             })

    retention_graph = retention_graph.sort_index().copy()

    print(retention_graph)

    retention_graph.plot(kind='line', x=periods_label, y=retention_label, figsize=(15, 10), marker='o')
    plt.title('Retention by time period', fontsize=35)

    plt.rcParams.update({'font.size': 25})
    plt.ylim([0, 1])
    plt.xlim([0, retention_graph[retention_label].max()])
    plt.xticks(np.arange(0, retention_graph[periods_label].max()+1), fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid()

    for index, row in retention_graph.iterrows():
        plt.text(row[periods_label], row[retention_label], round(row[retention_label]*100, 2), fontsize=25)


if __name__ == '__main__':
    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')
    events.add_period_to_data()

    config_path = '../retention/retention_config.json'
    with open(os.path.abspath(config_path), 'r') as f:
        config = json.load(f)
    config_events = config['events']

    # filter by event types from config
    event_types = et.load_event_types_from_json(config_events)
    if len(event_types) > 0:
        events.filter_by_event_type(event_types, add_event_type_name=True)

    events.data = events.data[[events.user_id_column, events.period_id_column]]
    events.data.drop_duplicates(inplace=True)

    events.data.set_index(events.user_id_column, inplace=True)

    retention = retention_by_period(events)
    plot_retention_by_period(retention)

    plt.show()


