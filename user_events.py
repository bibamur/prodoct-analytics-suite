import os
from typing import List

import pandas as pd
import json
from event_type import EventType
import event_type as et

class UserEvents:
    events_data_path: str
    timestamp_column: str
    user_id_column: str
    periods_data_path: str
    start_date: str
    end_date: str
    period_id_column: str
    data: pd.DataFrame

    def __init__(self, events_metadata_path, periods_metadata_path):
        with open(os.path.abspath(events_metadata_path), 'r') as f:
            events_metadata = json.load(f)

        with open(os.path.abspath(periods_metadata_path), 'r') as f:
            periods_metadata = json.load(f)

        # Set string constants from events metadata
        self.events_data_path = events_metadata['events_data_path']
        self.timestamp_column = events_metadata['timestamp_column']
        self.user_id_column = events_metadata['user_id_column']

        # Set string constants from periods metadata
        self.periods_data_path = periods_metadata['periods_data_path']
        self.start_date = periods_metadata['period_start']
        self.end_date = periods_metadata['period_end']
        self.period_id_column = periods_metadata['period_id']

    def load_user_events_data(self):
        events_path = self.events_data_path
        self.data = pd.read_csv(events_path)  # Load events data

    def add_period_to_data(self):
        periods_path = self.periods_data_path
        period_id_column = self.period_id_column
        start = self.start_date
        end = self.end_date
        timestamp = self.timestamp_column

        self.data[timestamp] = self.data[timestamp].astype(str).str[:-6]  # Remove timestamp from the date
        self.data[timestamp] = pd.to_datetime(self.data[timestamp])  # Change date type to datetime
        self.data.set_index(timestamp, inplace=True)  # Set date as index

        time_periods = pd.read_csv(periods_path, index_col=0)
        self.data[period_id_column] = 0

        for index, period in time_periods.iterrows():
            period_id = period[period_id_column]
            self.data.loc[period[start]:period[end], period_id_column] = period_id


def filter_by_event_type(user_events: UserEvents, types: List[EventType], add_event_type_name=False):
    data = user_events.data
    data_filter = pd.Series(False, index=data.index)
    if add_event_type_name:
        data[et.event_type_str] = ''
    for event_type in types:
        columns = list(event_type.conditions.keys())
        conditions = pd.Series(event_type.conditions)
        event_filter = (data[columns] == conditions).all(axis=1)
        if add_event_type_name:
            data.loc[event_filter, et.event_type_str] = event_type.name  # add event name to DataFrame
        data_filter |= event_filter
    return data[data_filter]


