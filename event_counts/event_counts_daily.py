from typing import Dict, List
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from user_events import UserEvents
import user_events as uev
from event_type import EventType
import event_type as et
import os
import json
from pandas.plotting import register_matplotlib_converters

# Set constants to use in the script
event_type_str = et.StringConstants.event_type.value



def counts_daily(user_events: UserEvents, types: List[EventType]) -> pd.DataFrame:
    """
    Calculates total number of events by event type by day
    Args:
        User Events instance
        list of event types
    Returns:
         DataFrame with total event counts
    """
    data = user_events.data
    timestamp_col = user_events.timestamp_column
    user_id = user_events.user_id_column
    tasks_counts = data.groupby([timestamp_col, event_type_str])[user_id].agg('count')
    tasks_counts = tasks_counts.reset_index()
    return tasks_counts


def uniques_daily(user_events: UserEvents, types: List[EventType]) -> pd.DataFrame:
    """
    Calculates number of unique users who performed the event by event type by date
    Args:
        User Events instance
        list of event types
    Returns:
         DataFrame with unique users counts
    """
    data = user_events.data
    timestamp_col = user_events.timestamp_column
    user_id = user_events.user_id_column
    unique_counts = data[[timestamp_col, event_type_str, user_id]].drop_duplicates()
    unique_counts = unique_counts.groupby([timestamp_col, event_type_str])[user_id].agg('count')
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
    x_coord = counts_df[period_id].unique()
    ax.set_xticks(x_coord)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=20)
    ax.set_ylabel(title)
    ax.set_title(title)
    ax.xaxis.set_tick_params(labelsize=18)
    ax.legend()


if __name__ == '__main__':


    events = uev.UserEvents.init_from_files(events_metadata_path='../data/events_metadata.json',
                                            periods_metadata_path='../data/periods_metadata.json')
    # Prepare data, set timestamp as index, keep only date in original timestamp column
    events.data[events.timestamp_column] = pd.to_datetime(events.data[events.timestamp_column])
    events.data.set_index(events.timestamp_column, inplace=True, drop=False)
    del events.data.index.name
    events.data[events.timestamp_column] = events.data[events.timestamp_column].apply(lambda x: datetime.date(x))

    # filter data by start/end dates and event types in question
    config_path = '../event_counts/event_counts_config.json'
    with open(os.path.abspath(config_path), 'r') as f:
        config = json.load(f)
    config_events = config['events']
    period_start_date = config['start_date']
    period_end_date = config['end_date']
    events.data = events.data.loc[period_start_date:period_end_date]

    event_types = et.load_event_types_from_json(config_events)
    if len(event_types) > 0:
        events.filter_by_event_type(event_types, add_event_type_name=True)

    total_df = counts_daily(events, event_types)
    unique_df = uniques_daily(events, event_types)

    # plot daily counts
    register_matplotlib_converters()
    plt.rcParams.update({'font.size': 22})

    fig, axs = plt.subplots(2)
    plot_event_counts(total_df, event_types, axs[0], events.timestamp_column, events.user_id_column,
                      'Total number of events.')

    plot_event_counts(unique_df, event_types, axs[1], events.timestamp_column, events.user_id_column,
                      'Total number of unique users.')

    plt.show()
