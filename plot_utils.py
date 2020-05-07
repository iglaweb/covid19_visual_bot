from collections import defaultdict
from datetime import datetime
from typing import Tuple, Any, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter

import virus_utils
from models import StatType, Country


def generate_world_stat_10(stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    most_areas = get_most_countries(data, stat_type)

    fig, ax = plt.subplots()

    for k, v in most_areas:
        x = []
        y = []
        for date in v[0]['dates']:
            date_str = date['date']
            group = date_str.split("-")
            year = virus_utils.num(group[0])
            month = virus_utils.num(group[1])
            day = virus_utils.num(group[2])
            dt = datetime(year=year, month=month, day=day)

            x.append(dt)
            cell_value = date[stat_type.to_name()]
            y.append(virus_utils.num(cell_value))
        ax.plot(x, y, label=v[0]['title'])  # for each country

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    plt.grid(True)
    plt.xlabel('Day')
    plt.ylabel(stat_type.to_name().title())
    plt.legend(loc="upper left")
    return fig, ax


def show_deaths_stat_10(stat_type: StatType):
    generate_world_stat_10(stat_type)
    plt.show()


def generate_bar_world_stat_10(stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    dct = defaultdict(list)
    for country_title, dates in data.items():
        total = dates[-1][stat_type.to_name()]  # just last element
        dct[total].append(country_title)

    sorted_dict = sorted(dct.items(), reverse=True)
    most_areas = sorted_dict[:10]  # 10 most countries
    most_areas.reverse()  # show most first

    x = []
    y = []
    for num, count in most_areas:
        title = count[0]
        x.append(title)
        y.append(int(num))

    y_pos = np.arange(len(x))

    fig, ax = plt.subplots()
    ax.barh(y_pos, y, align='center', alpha=0.5)

    ax.set_yticklabels(x)
    ax.set_yticks(np.arange(len(x)))

    ax.set_xlabel(stat_type.to_name().title())
    ax.set_title(f'{stat_type.to_name().title()} statistics – 10 Most Countries')

    for i, count in enumerate(y):
        ax.text(count, i, " " + f'{count:,}', color='blue', va='center')  # print big nums with comma
    return fig, ax


def fetch_country_data(country: Country) -> Optional[any]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    country_id = country.serverId
    country = data.get(country_id)
    if country is None:
        print(f'Country {country_id} not found')
        return None
    return country


def get_datetime_obj(item: any) -> datetime:
    date_str = item['date']
    group = date_str.split("-")
    year = virus_utils.num(group[0])
    month = virus_utils.num(group[1])
    day = virus_utils.num(group[2])
    dt = datetime(year=year, month=month, day=day)
    return dt


fs = lambda m, n: [i * n // m + n // (2 * m) for i in range(m)]


def generate_country_active_plot(country: Country, stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    country_data = fetch_country_data(country)
    if country_data is None:
        return None
    country_name = country.title

    fig, ax = plt.subplots()
    x = []
    y = []
    for idx, item in enumerate(country_data):
        cell_value = virus_utils.num(item[stat_type.to_name()])
        if cell_value < 1:
            continue
        # since api means only total values
        cell_value_prev = cell_value if idx == 0 else virus_utils.num(country_data[idx - 1][stat_type.to_name()])
        actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
        if actual_diff == 0:  # skip
            continue

        dt = get_datetime_obj(item)
        x.append(dt)
        y.append(actual_diff)

    ax.plot(x, y, marker='', color='#EF7028', linewidth=2.5, label=country_name)  # for each country

    # if len(x) > 40:
    #     idx_arr = fs(40, len(x))  # 30 from all items
    #     x_new = []
    #     y_new = []
    #     for idx in idx_arr:
    #         x_new.append(x[idx])
    #         y_new.append(y[idx])
    #     x = x_new
    #     y = y_new
    # ax.xaxis.set_major_locator(plt.MaxNLocator(3))
    # ax.yaxis.set_major_locator(plt.MaxNLocator(3))

    ax.set_ylabel(stat_type.to_name().title())
    ax.set_title(f'{country_name} – Daily New {stat_type.to_name().title()}')

    bar = ax.bar(x, y, zorder=3, alpha=0.65, color='#b2b2b2')  # grid behind the bars
    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    # zip joins x and y coordinates in pairs
    for xs, ys in zip(x, y):
        label = ys
        plt.annotate(label,  # this is the text
                     (xs, ys),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(-10, 0),  # distance from text to points (x,y)
                     ha='right')  # horizontal alignment can be left, right or center

    # draw_text_bar_vert(bar)
    plt.tight_layout()

    return fig, ax


def get_axis_avg_plot(country_data, stat_type: StatType):
    x = []
    y = []
    avg = []
    summa = 0
    window_size = 7

    skip_first_empty = True  # skip first empty data
    for idx, item in enumerate(country_data):
        cell_value = virus_utils.num(item[stat_type.to_name()])
        if skip_first_empty and cell_value < 1:
            continue

        skip_first_empty = False
        # since api means only total values
        cell_value_prev = cell_value if idx == 0 else virus_utils.num(country_data[idx - 1][stat_type.to_name()])
        actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
        if actual_diff == 0:  # skip
            continue

        index = len(y)
        dt = get_datetime_obj(item)
        x.append(dt)
        y.append(actual_diff)

        summa = summa + actual_diff
        if index >= window_size:
            summa = summa - y[index - window_size]  # throw away first edge
            avg_val = summa / window_size
        else:
            avg_val = summa / len(y)
        avg.append(avg_val)

    return x, avg


def generate_country_toll_plot_avg(country: Country, stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    country_data = fetch_country_data(country)
    if country_data is None:
        return None
    country_name = country.title

    fig, ax = plt.subplots()

    x, avg = get_axis_avg_plot(country_data, stat_type)
    ax.plot(x, avg, marker='', color='#EF7028', linewidth=2.5, label=country_name)  # for each country

    ax.set_ylabel(stat_type.to_name().title())
    ax.set_title(f'{country_name} – {stat_type.to_name().title()} (7-day rolling average)')

    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically
    return fig, ax


def get_most_countries(data: any, stat_type: StatType) -> list:
    # get only 10 most countries
    dct = defaultdict(list)
    for country_title, dates in data.items():
        total = dates[-1][stat_type.to_name()]  # just last element
        dct[total].append({'title': country_title, 'dates': dates})

    sorted_dict = sorted(dct.items(), reverse=True)
    return sorted_dict[:10]  # 10 most countries


def generate_toll_plot_avg(stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    # get only 10 most countries
    most_areas = get_most_countries(data, stat_type=stat_type)

    fig, ax = plt.subplots()
    for k, v in most_areas:
        country_name = v[0]['title']
        country_data = v[0]['dates']

        x, avg = get_axis_avg_plot(country_data=country_data, stat_type=stat_type)
        ax.plot(x, avg, label=country_name)  # for each country

        # draw text of the country near the last point
        # if len(x) > 0:
        #  point = (x[len(x) - 1], avg[len(avg) - 1])
        #  ax.annotate(country_name, point)

    ax.set_ylabel(stat_type.to_name().title())
    ax.set_title(f'{stat_type.to_name().title()} (7-day rolling average)')

    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    plt.grid(True)
    plt.xlabel('Day')
    plt.ylabel(stat_type.to_name().title())
    plt.legend(loc="upper left")

    return fig, ax


def draw_text_bar_vert(bar: Any):
    # Add counts above the two bar graphs
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height, '%d' % int(height), ha='center', va='bottom')


def generate_country_total_plot(country: Country, stat_type: StatType) -> Optional[
    Tuple[Any, Any]]:
    # show_only_weeks = stat_type == StatType.CONFIRMED  # too much data to draw
    country_data = fetch_country_data(country)
    if country_data is None:
        return None
    country_name = country.title

    fig, ax = plt.subplots()
    x = []
    y = []
    for item in country_data:
        cell_value = virus_utils.num(item[stat_type.to_name()])
        if cell_value < 1:
            continue

        dt = get_datetime_obj(item)
        x.append(dt)

        # if show_only_weeks is False or dt.weekday() == 0:  # monday only or add all, decrease data
        y.append(cell_value)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))

    ax.plot(x, y, marker='', color='#EF7028', linewidth=2.5, label=country_name)  # for each country

    ax.set_ylabel(stat_type.to_name().title())
    ax.set_title(f'{country_name} – {stat_type.to_name().title()} Total statistics')

    bar = ax.bar(x, y, zorder=3, alpha=0.65, color='#b2b2b2')  # grid behind the bars
    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    # Add counts above the two bar graphs
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height, '%d' % int(height), ha='center', va='bottom')
    plt.tight_layout()

    return fig, ax


def show_stat_new(country_name: Country, stat_type: StatType):
    country = fetch_country_data(country_name)
    if country is None:
        return None

    x = []
    y = []
    cnt = 0
    for item in country:
        cnt += 1
        x.append(cnt)
        if stat_type == StatType.DEATHS:
            y.append(item['deaths'])
        elif stat_type == StatType.CONFIRMED:
            y.append(item['confirmed'])
        else:
            y.append(item['recovered'])

    plt.plot(x, y)
    plt.xlabel('Day')

    if stat_type == StatType.DEATHS:
        plt.ylabel('Deaths')
    elif stat_type == StatType.CONFIRMED:
        plt.ylabel('Confirmed')
    else:
        plt.ylabel('Recovered')

    plt.show()


def show_deaths_stat_new(country_name: Country):
    show_stat_new(country_name, StatType.DEATHS)


def show_cases_stat_new(country_name: Country):
    show_stat_new(country_name, StatType.CONFIRMED)


def show_recovered_stat_new(country_name: Country):
    show_stat_new(country_name, StatType.RECOVERED)


def show_deaths_stat(country: Country):
    country_name = country.serverId
    data = virus_utils.fetch_timeseries_report_deaths()
    if len(data) > 0:
        country_name = country_name.lower()
        found_country = None
        for item in data:
            name = item.get_location_name().lower()
            if country_name == name:
                found_country = item

        if country_name is None:
            print('Such country is not found')
            return

        x = []
        y = []
        cnt = 0
        for k, v in found_country.dates.items():
            cnt += 1
            x.append(cnt)
            y.append(v)

        plt.plot(x, y)
        plt.xlabel('Day')
        plt.ylabel('Deaths')
        plt.show()


def show_deaths_most_10():
    data = virus_utils.fetch_timeseries_report_deaths()
    x = []
    y = []

    dct = defaultdict(list)
    for item in data:
        dct[item.total].append(item.get_location_name())

    sorted_dict = sorted(dct.items(), reverse=True)
    most_areas = sorted_dict[:10]

    for k, v in most_areas:
        y.append(k)
        x.append(v[0])

    objects = x
    y_pos = np.arange(len(objects))
    performance = y

    plt.barh(y_pos, performance, align='center', alpha=0.5)
    plt.yticks(y_pos, objects)
    plt.xlabel('Deaths')
    plt.title('Deaths statistics – 10 Most Countries')

    for i, v in enumerate(performance):
        plt.text(v, i, " " + str(v), color='blue', va='center')

    plt.show()
