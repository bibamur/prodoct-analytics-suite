from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List

import pandas as pd
import json
from event_type import EventType
import event_type as et


@dataclass
class UserEvents:
    timestamp_column: str
    user_id_column: str
    periods_data_path: str
    start_date: str
    end_date: str
    period_id_column: str
    data: pd.DataFrame
    time_periods: pd.DataFrame

    @classmethod
    def init_from_files(cls, events_metadata_path: str, periods_metadata_path: str) -> UserEvents:
        with open(os.path.abspath(events_metadata_path), 'r') as f:
            events_metadata = json.load(f)

        with open(os.path.abspath(periods_metadata_path), 'r') as f:
            periods_metadata = json.load(f)

        data = pd.read_csv(events_metadata['events_data_path'])  # Load events data

        # Set string constants from events metadata

        return cls(data=data,
                   timestamp_column=events_metadata['timestamp_column'],
                   user_id_column=events_metadata['user_id_column'],

                   # Set string constants from periods metadata
                   periods_data_path=periods_metadata['periods_data_path'],
                   start_date=periods_metadata['period_start'],
                   end_date=periods_metadata['period_end'],
                   period_id_column=periods_metadata['period_id'],
                   time_periods = pd.DataFrame())

    def add_period_to_data(self):
        periods_path = self.periods_data_path
        period_id_column = self.period_id_column
        start = self.start_date
        end = self.end_date
        timestamp = self.timestamp_column

        self.data[timestamp] = pd.to_datetime(self.data[timestamp])  # Change date type to datetime
        self.data.set_index(timestamp, inplace=True)  # Set date as index

        self.time_periods = pd.read_csv(periods_path, index_col=0)
        self.data[period_id_column] = 0

        for index, period in self.time_periods.iterrows():
            period_id = period[period_id_column]
            self.data.loc[period[start]:period[end], period_id_column] = period_id

    def filter_by_event_type(self, types: List[EventType], add_event_type_name=False):
        event_type_str = et.StringConstants.event_type.value
        data_filter = pd.Series(False, index=self.data.index)
        if add_event_type_name:
            self.data[event_type_str] = ''
        for event_type in types:
            columns = list(event_type.conditions.keys())
            conditions = pd.Series(event_type.conditions)
            event_filter = (self.data[columns] == conditions).all(axis=1)
            if add_event_type_name:
                self.data.loc[event_filter, event_type_str] = event_type.name  # add event name to DataFrame
            data_filter |= event_filter
        self.data = self.data[data_filter]


