# Basic tools for Product Analytics 

This repository contains basic tools for product analytics and open for everyone who would like to use it.
The approach to the analysis is based on the model of user events: each event is a particular action performed by user in the product.

[You can see the detailed description of the tools in the project's wiki.](https://github.com/bibamur/product-analytics-suite/wiki) 

#### Following tools are included in this repository:
1. Histogram ('../hist/hist.py')
2. Event counts - total and unique 
    - Daily counts ('../event_counts/event_counts_daily.py')
    - Counts by Period ('../event_counts/event_counts_by_period.py')
3. Retention 
    - Daily retention ('../retention/retention_daily.py')
    - Retention by period ('../retention/retention_daily.py')
4. Funnels ('../funnels/funnels.py')


# How to execute:

#### Prepare data files:
    - File with events
    - File with time periods - needed for Counts by period and Retention by period calculation.  Period ID is mandatory column in time periods file, *must be ascending integrer for correct retention by period calculation*

#### Prepare metadata files - should have exact same structure as provided in the project.


1. Events metadata file ('../data/events_metadata.json') should contain following fields:
- events_data_path: path to data
- timestamp_column: name of the column containing timestamp (mandatory column in events file)
- user_id_column:name of the column containing user_id  (mandatory column in events file)


2.Time periods metadata file ('../data/periods_metadata.json') should have same ecact structure as in the project.
- periods_data_path: path to time periods data
- period_id: name of the column with period ID in time periods data (mandatory column in time periods file, *must be ascending integrer for correct retention by period calculation*)
- period_start: name of the column with period start date in time periods data (mandatory column in time periods file)
- period_end: name of the column with period end date in time periods data (mandatory column in time periods file)


#### Prepare configuration files for particular scripts.


1. Histogram config ('../hist/hist_config.json') contains list of events to calculate histogram for. Each event is described by:
- name: event name
- conditions: list of conditions that should be applied to events to get necessary events. Each condition consists of events file column name and value.

2. Event counts config ('../event_counts/event_counts_config.json') contains:
    - start_date: start date for daily events count script (events performed during start date are included)
    - end_date: end date for daily events count script (events performed during end date are included)
    - list of events to count

3. Retention config ('../'retention/retention_config.json) contains:
- events: List of events to calculate retention for
- start_date: start date of the period of the first user event for daily retention script (if user performed her first event during start day, this day will be counted as retention day 0)
- end_date: end date of the period of the first user event  for daily retention script (if user performed her first event during end day, this day will be counted as retention day 0)

4. Funnels config ('../funnels/funnels_config.json') contains list of funnel events. 
- *Order is important in this config file, as it defines oreder of events in funnel!* Each event also defined with event name and conditions


Once everything is prepared, execute each script to get corresponding visualisation.
