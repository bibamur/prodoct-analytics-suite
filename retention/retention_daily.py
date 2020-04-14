# -*- coding: utf-8 -*-
import json
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import user_events as uev
from user_events import UserEvents
import numpy as np
import event_type as et


def calculate_daily_retention(users: np.ndarray, events: uev.UserEvents):
    user_retention_days_dict = {}

    for user in users:
        user_dates = events.data.loc[events.data[events.user_id_column] == user, events.timestamp_column].values
        dates = pd.to_datetime(user_dates)
        if not dates.empty:
            min_timestamp = min(dates)
            dates = pd.Series(((dates - min_timestamp).days).drop_duplicates().sort_values())
            user_retention_days_dict[user] = dates
    user_retention_days = pd.concat(user_retention_days_dict.values())

    return user_retention_days


def get_users_with_first_event_in_period(events: UserEvents, start: str, end: str):
    users_first_event_date = events.data.groupby(events.user_id_column)[events.timestamp_column].min()
    users_first_event_date = pd.Series(users_first_event_date.index.values,
                                       index=users_first_event_date)  # swap index and value in Series
    users_with_first_event = users_first_event_date[start:end].values
    return users_with_first_event


def plot_daily_retention(ax: plt.Axes, retention_days: pd.Series):
    daily_retention = pd.DataFrame(
        {'Ret N': retention_days.value_counts(),
         'Ret %': retention_days.value_counts() / retention_days.value_counts().max()
         }
    ).sort_index()

    for index, row in daily_retention.iterrows():
        # print(row['Number of users'])
        if index % 7 != 0: continue  # show annotation for evety 7th day
        plt.text(index, row['Ret %'], round(row['Ret %'] * 100, 2))

    plt.rcParams.update({'font.size': 15})
    plt.xticks(daily_retention.index.values)
    plt.plot(daily_retention['Ret %'], marker='o', color='blue')

    ax.xaxis.set_major_locator(plt.MaxNLocator(50))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))

    plt.ylim([0, 1])
    plt.xlim([0, daily_retention.index.max()])
    plt.title('Daily retention graph', fontsize=35)
    blue_line = mlines.Line2D([], [], color='blue',
                              label='Total users count: ' + str(len(users)) + '\nStart date: ' + str(
                                  start_date) + '\nEnd date: ' + str(end_date))
    plt.legend(handles=[blue_line], fontsize=25)
    plt.xlabel('Retention Day N', fontsize=35)
    plt.ylabel('Retention %', fontsize=35)

    plt.grid()


if __name__ == '__main__':
    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')
    events.data[events.timestamp_column] = pd.to_datetime(events.data[events.timestamp_column])

    # read config
    config_path = '../retention/retention_config.json'
    with open(os.path.abspath(config_path), 'r') as f:
        config = json.load(f)
    config_events = config['events']
    start_date = config['start_date']
    end_date = config['end_date']

    # filter by event types from config
    event_types = et.load_event_types_from_json(config_events)
    if len(event_types) > 0:
        events.filter_by_event_type(event_types, add_event_type_name=True)

    users = get_users_with_first_event_in_period(events, start_date, end_date)
    user_retention_days = calculate_daily_retention(users, events)


    ax = plt.axes()
    plot_daily_retention(ax, user_retention_days)

    plt.show()
