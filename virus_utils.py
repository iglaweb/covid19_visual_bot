import csv
import datetime
import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime
from io import StringIO
from typing import Optional

import requests
from dateutil.parser import parse as parsedate

import io_utils
from models import Country, Countries
from virus_model import TimeSeriesItem

timeseries_url = 'https://pomber.github.io/covid19/timeseries.json'


def num(s):
    try:
        return int(s)
    except ValueError:
        return 0


TIMOUT_SEC = 3 * 60 * 60  # 3 hours in seconds

pref_country_persist = {}


def read_prefs() -> Optional[dict]:
    if os.path.exists(io_utils.get_prefs_path()) is False:
        return {}
    with open(io_utils.get_prefs_path(), 'r') as fp:
        return json.load(fp)


def write_config(data):
    with open(io_utils.get_prefs_path(), 'w') as fp:
        json.dump(data, fp)


def read_pref_country(user_id: int) -> Country:
    country = pref_country_persist.get(user_id)
    if country is None:
        return Countries.US  # default value
    return Countries[country]


def write_pref_country(user_id: int, country: Countries):
    pref_country_persist[user_id] = country.displayValue


def read_pref_date() -> int:
    if os.path.exists(io_utils.get_prefs_path()) is False:
        return 0
    config = read_prefs()
    datetime_val = config.get('datetime')  # not square
    if datetime_val is None:
        return 0
    return int(datetime_val)


def write_pref_date(date: int):
    config = read_prefs()
    config['datetime'] = str(date)
    write_config(config)


def is_remote_file_changed(since_timestamp: int) -> bool:
    r = requests.head(timeseries_url)
    if r.status_code == requests.codes.ok:
        url_time = r.headers['last-modified']
        url_date = parsedate(url_time)
        url_date_sec_epoch = int(time.mktime(url_date.timetuple()))
        return url_date_sec_epoch > since_timestamp
    return True  # default changed


def should_update_data() -> bool:
    if os.path.exists(io_utils.get_data_path()) is False:  # no source data exists
        return True
    sec_now = int(time.time())  # current time
    last_time_update_sec = int(os.path.getmtime(io_utils.get_data_path()))
    timeout_expired = sec_now - last_time_update_sec >= TIMOUT_SEC  # need to update date
    if timeout_expired is False:
        return False  # file is already up to date

    datetime_stamp = read_pref_date()
    is_remote_changed = is_remote_file_changed(datetime_stamp)
    return is_remote_changed


def fetch_pomper_stat() -> Optional[dict]:
    should_refresh = should_update_data()
    if should_refresh is False:
        # try to return cached data
        if os.path.exists(io_utils.get_data_path()):
            with open(io_utils.get_data_path()) as json_file:
                data = json.load(json_file)
                return data

    req = requests.get(timeseries_url)
    if req.status_code == requests.codes.ok:
        # save datetime
        date_timestamp = req.headers['last-modified']
        url_date = parsedate(date_timestamp)

        ts = time.mktime(url_date.timetuple())
        write_pref_date(int(ts))

        json_data = req.json()
        # save file
        with open(io_utils.get_data_path(), 'w') as outfile:  # create or overwrite
            json.dump(json_data, outfile)
        return json_data  # the response is a JSON
    return None


def fetch_timeseries_report_deaths() -> Optional[list]:
    return fetch_timeseries_report('time_series_covid19_deaths_global.csv')


def fetch_timeseries_report_recovered() -> Optional[list]:
    return fetch_timeseries_report('time_series_covid19_recovered_global.csv')


def fetch_timeseries_report_confirmed() -> Optional[list]:
    return fetch_timeseries_report('time_series_covid19_confirmed_global.csv')


def fetch_timeseries_report(file_name: str) -> Optional[list]:
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
          f'/csse_covid_19_time_series/{file_name}'
    req = requests.get(url)
    if req.status_code == requests.codes.ok:

        csv_content = req.text

        data_stats = []
        csv_file = StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                print(f'Column names are {", ".join(row)}')

            total = 0
            dates_stat = defaultdict(int)
            for key, value in row.items():
                # print(key)
                match = re.search(r'\d{1,2}/\d{1,2}/\d{2}', key)
                if match is not None:
                    group = match.group().split("/")
                    year = 2000 + num(group[2])
                    month = num(group[0])
                    day = num(group[1])
                    dt = datetime(year=year, month=month, day=day)
                    # date = datetime.strptime(match.group(), '%-m/%d/%y').date()
                    print(dt)
                    date_str = dt.isoformat()
                    dates_stat[date_str] = num(value)
                    total += num(value)

            country = row["Country/Region"]
            state = row["Province/State"]
            ts = TimeSeriesItem(state, country, dates_stat, total)
            data_stats.append(ts)
            # print(f'\t country: {row["Country/Region"]} {row["Province/State"]} ')

            line_count += 1
        print(f'Processed {line_count} lines.')
        return data_stats

    return None


def reformat_large_tick_values(tick_val, pos):
    """
    Turns large tick values (in the billions, millions and thousands) such as 4500 into 4.5K and also appropriately turns 4000 into 4K (no zero after the decimal).
    """
    if tick_val >= 1000000000:
        val = round(tick_val / 1000000000, 1)
        new_tick_format = '{:}B'.format(val)
    elif tick_val >= 1000000:
        val = round(tick_val / 1000000, 1)
        new_tick_format = '{:}M'.format(val)
    elif tick_val >= 1000:
        val = round(tick_val / 1000, 1)
        new_tick_format = '{:}K'.format(val)
    elif tick_val < 1000:
        new_tick_format = round(tick_val, 1)
    else:
        new_tick_format = tick_val

    # make new_tick_format into a string value
    new_tick_format = str(new_tick_format)

    # code below will keep 4.5M as is but change values such as 4.0M to 4M since that zero after the decimal isn't needed
    index_of_decimal = new_tick_format.find(".")

    if index_of_decimal != -1:
        value_after_decimal = new_tick_format[index_of_decimal + 1]
        if value_after_decimal == "0":
            # remove the 0 after the decimal point since it's not needed
            new_tick_format = new_tick_format[0:index_of_decimal] + new_tick_format[index_of_decimal + 2:]

    return new_tick_format
