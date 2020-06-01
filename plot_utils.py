from collections import defaultdict
from datetime import datetime
from typing import Tuple, Any, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter

import io_utils
import virus_utils
from models import StatType, Country

fs = lambda m, n: [i * n // m + n // (2 * m) for i in range(m)]


def parse_date(date_str: str) -> datetime:
    group = date_str.split("-")
    year = virus_utils.num(group[0])
    month = virus_utils.num(group[1])
    day = virus_utils.num(group[2])
    return datetime(year=year, month=month, day=day)


def generate_world_mortality_rate_10() -> Optional[Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    dct = defaultdict(float)
    dct_dates = defaultdict(list)
    data_items = data.items()
    for country_title, dates in data_items:
        if country_title == 'MS Zaandam':
            continue  # skip ship liner
        latest_date = dates[-1]
        confirmed = latest_date[StatType.CONFIRMED.to_data_name()]  # just last element
        deaths = latest_date[StatType.DEATHS.to_data_name()]  # just last element
        if confirmed == 0: continue
        mortality_rate: float = deaths / confirmed
        dct[country_title] = mortality_rate
        dct_dates[country_title] = dates

    sorted_dict = sorted(dct.items(), key=lambda k_v: k_v[1], reverse=True)
    most_areas = sorted_dict[:10]  # 10 most countries

    fig, ax = plt.subplots()

    for k, v in most_areas:
        country_title = k
        country_data = dct_dates[k]
        if country_data is not None:
            x = []
            y = []
            for date in country_data:
                confirmed = date[StatType.CONFIRMED.to_data_name()]  # just last element
                deaths = date[StatType.DEATHS.to_data_name()]  # just last element
                if confirmed == 0: continue
                mortality_rate: float = deaths / confirmed

                cell_value = mortality_rate * 100  # convert to percent
                date_str: str = date['date']
                dt: datetime = parse_date(date_str)
                x.append(dt)
                y.append(cell_value)

            ax.plot(x, y, label=country_title)  # for each country

    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{val:d}{suffix}'.format(val=int(y), suffix='%')))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(f'Day\nData updated: {date_update_str}')
    plt.ylabel('Fatality rate')
    plt.legend(loc="upper left")

    ax.set_title('Fatality rate of COVID-19 pandemic')
    return fig, ax


def generate_world_stat_10(stat_type: StatType, active: bool = False, country: Country = None,
                           ax: any = None) -> Optional[
    Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    most_areas = get_most_countries(data, stat_type)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = None

    country_data = None
    for k, v in most_areas:
        x = []
        y = []
        idx = -1
        dates = v[0]['dates']
        for date in dates:
            idx = idx + 1
            cell_value = virus_utils.num(date[stat_type.to_data_name()])

            add_val: int
            if active:
                if cell_value < 1:
                    continue
                # since api means only total values
                cell_value_prev = cell_value if idx == 0 else virus_utils.num(
                    dates[idx - 1][stat_type.to_data_name()])
                actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
                add_val = actual_diff
            else:
                add_val = cell_value
            y.append(add_val)

            date_str = date['date']
            dt = parse_date(date_str)
            x.append(dt)

        country_title = v[0]['title']
        line_width = 1
        if country is not None:  # highlight country line
            if country.serverId == country_title:
                line_width = 2.5
                country_data = dates
            else:
                line_width = 0.8

        ax.plot(x, y, linewidth=line_width, label=country_title)  # for each country

    # calc values
    avg = 0
    if country_data is not None:
        count = 0
        summa = 0
        cell_value_prev = 0
        for date in country_data[::-1]:
            if count > 7:
                break
            cell_value = virus_utils.num(date[stat_type.to_data_name()])
            if count > 0:
                actual_diff = abs(cell_value_prev - cell_value)
                summa = summa + actual_diff

            cell_value_prev = cell_value
            count = count + 1

        avg = 0 if count == 0 else summa // count

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)

    if fig is not None:
        fig.autofmt_xdate()  # Rotate date labels automatically

    # Show the major grid lines with dark grey lines
    ax.grid(b=True, which='major', color='#666666', linestyle='-')

    ax.minorticks_on()
    ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(f'Day\nData updated: {date_update_str}')
    plt.ylabel(stat_type.to_title().title())
    ax.legend(loc='best')

    country_label = '10 Most Countries' if country is None else f'{country.title} (avg per last 7 days = {avg})'
    ax.set_title(f'{stat_type.to_title().title()} Statistics – {country_label}')
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
        total = dates[-1][stat_type.to_data_name()]  # just last element
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

    # format big values
    ax.xaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    ax.set_xlabel(f'{stat_type.to_title().title()}\nData updated: {date_update_str}')
    ax.set_title(f'{stat_type.to_title().title()} statistics – 10 Most Countries')

    for i, count in enumerate(y):
        ax.text(count, i, " " + f'{count:,}', color='black', va='center')  # print big nums with comma

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
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
    return parse_date(date_str)


def generate_country_active_plot(country: Country, stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    country_data = fetch_country_data(country)
    if country_data is None:
        return None
    country_name = country.title

    fig, ax = plt.subplots()
    x = []
    y = []
    y_recovered = []
    for idx, item in enumerate(country_data):
        cell_value = virus_utils.num(item[stat_type.to_data_name()])
        if cell_value < 1:
            continue
        # since api means only total values
        cell_value_prev = cell_value if idx == 0 else virus_utils.num(country_data[idx - 1][stat_type.to_data_name()])
        actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
        if actual_diff == 0:  # skip
            continue

        dt = get_datetime_obj(item)
        x.append(dt)
        y.append(actual_diff)

        if stat_type == StatType.CONFIRMED:
            cell_value_r = virus_utils.num(item[StatType.RECOVERED.to_data_name()])
            cell_value_prev_r = cell_value_r if idx == 0 else virus_utils.num(
                country_data[idx - 1][StatType.RECOVERED.to_data_name()])
            actual_diff_r = cell_value_r if idx == 0 else max(cell_value_r - cell_value_prev_r, 0)
            y_recovered.append(actual_diff_r)

    ax.plot(x, y, marker='', linewidth=1.5, label=stat_type.to_title().title())  # for each country
    if len(y_recovered) > 0:
        ax.plot(x, y_recovered, marker='', linewidth=1.5,
                label=StatType.RECOVERED.to_title().title())  # for each country
        plt.legend(loc="upper left")

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(f'Data updated: {date_update_str}')

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'{country_name} – Daily {stat_type.to_title().title()}')

    ax.xaxis_date()
    ax.grid(zorder=0)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    # draw_text_bar_vert(bar)
    plt.tight_layout()
    return fig, ax


def generate_country_active_plot_per_million(country: Country, stat_type: StatType) -> Optional[
    Tuple[Any, Any]]:
    country_data = fetch_country_data(country)
    if country_data is None:
        return None

    country_name = country.title
    fig, ax = plt.subplots()

    people = io_utils.get_population(country_name)
    if people == 0:  # no such country
        return None
    person_per_million = people // 1_000_000  # e.g. Russia: 145
    op_calc_val = lambda y: return_per_million_val(y, person_per_million)
    x, y = get_axis_avg_week_plot(country_data, stat_type, op_calc_val, False)

    ax.plot(x, y, marker='', color='#EF7028', linewidth=2.5, label=country_name)  # for each country

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'{country_name} – Daily {stat_type.to_title().title()} per million inhabitants')
    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    plt.tight_layout()
    return fig, ax


def get_plot_country_per_million(country_data: list, stat_type: StatType, person_per_million: int, fun, *args,
                                 use_date=False):
    x = []
    y = []
    counter = 0
    for idx, item in enumerate(country_data):
        cell_value = virus_utils.num(item[stat_type.to_data_name()])
        if cell_value < 1:
            continue
        # since api means only total values
        cell_value_prev = cell_value if idx == 0 else virus_utils.num(country_data[idx - 1][stat_type.to_data_name()])
        actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
        if actual_diff == 0:  # skip
            continue

        cases_per_million = actual_diff // person_per_million  # Russia avg=10k, 10k / 145
        if cases_per_million < 3:  # show only those that reached 3 cases per million
            continue

        if use_date:
            dt = get_datetime_obj(item)
            x.append(dt)
        else:
            counter = counter + 1
            x.append(counter)
        y.append(cases_per_million)
    return x, y


def generate_world_stat_10_per_million(stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    data = virus_utils.fetch_pomper_stat()
    if data is None:
        print('Data is not found')
        return None

    most_areas = get_most_countries(data, stat_type)
    fig, ax = plt.subplots()

    for k, v in most_areas:
        country_name = v[0]['title']
        dates = v[0]['dates']
        people = io_utils.get_population(country_name)
        if people == 0:  # no such country
            continue
        person_per_million = people // 1_000_000  # e.g. Russia: 145

        # pass custom function to calc Y value
        op_calc_val = lambda y: return_per_million_val(y, person_per_million)
        x, y = get_axis_avg_week_plot(dates, stat_type, op_calc_val, False)

        ax.plot(x, y, label=country_name)  # for each country

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'Daily COVID-19 {stat_type.to_title().title()} per million inhabitants')

    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(
        f'Day number after reaching 3 {stat_type.to_title().lower()} per million inhabitants\nData updated: {date_update_str}')
    plt.legend(loc="upper left", prop={'size': 10})
    return fig, ax


def return_input_arg(val: int) -> int:
    return val


def return_per_million_val(val: int, person_per_million: int) -> int:
    return val // person_per_million  # e.g. Russia avg in May cases=10k, 10k / 145


def get_axis_avg_week_plot(country_data: list, stat_type: StatType, op_calc_val=lambda y: return_input_arg(y),
                           use_date: bool = True):
    x = []
    y = []
    avg_y = []
    summa = 0
    window_size = 7

    counter = 0
    skip_first_empty = True  # skip first empty data
    for idx, item in enumerate(country_data):
        counter = counter + 1
        cell_value = virus_utils.num(item[stat_type.to_data_name()])
        if skip_first_empty and cell_value < 1:
            continue

        skip_first_empty = False
        # since api means only total values
        cell_value_prev = cell_value if idx == 0 else virus_utils.num(country_data[idx - 1][stat_type.to_data_name()])
        actual_diff = cell_value if idx == 0 else max(cell_value - cell_value_prev, 0)
        if actual_diff == 0:  # skip
            continue

        index = len(y)
        y.append(actual_diff)

        summa = summa + actual_diff
        if index >= window_size:
            summa = summa - y[index - window_size]  # throw away first edge
            avg_val = summa // window_size
        else:
            avg_val = summa // len(y)

        output = op_calc_val(avg_val)
        if output < 3:  # skip almost empty values
            continue

        if use_date:
            dt = get_datetime_obj(item)
            x.append(dt)
        else:
            x.append(counter)
        avg_y.append(output)

    return x, avg_y


def generate_country_toll_plot_avg(country: Country, stat_type: StatType) -> Optional[Tuple[Any, Any]]:
    country_data = fetch_country_data(country)
    if country_data is None:
        return None
    country_name = country.title

    fig, ax = plt.subplots()

    x, avg_y = get_axis_avg_week_plot(country_data=country_data, stat_type=stat_type, use_date=True)
    ax.plot(x, avg_y, marker='', color='#EF7028', linewidth=2.5, label=country_name)  # for each country

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'{country_name} – {stat_type.to_title().title()} (7-day rolling average)')
    ax.xaxis_date()

    # Show the major grid lines with dark grey lines
    plt.grid(zorder=0, b=True, which='major', color='#666666', linestyle='-')

    plt.minorticks_on()
    plt.grid(zorder=0, b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically
    return fig, ax


def get_most_countries(data: any, stat_type: StatType) -> list:
    # get only 10 most countries
    dct = defaultdict(list)
    for country_title, dates in data.items():
        total = dates[-1][stat_type.to_data_name()]  # just last element
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

        x, avg = get_axis_avg_week_plot(country_data=country_data, stat_type=stat_type, use_date=True)
        ax.plot(x, avg, label=country_name)  # for each country

        # draw text of the country near the last point
        # if len(x) > 0:
        #  point = (x[len(x) - 1], avg[len(avg) - 1])
        #  ax.annotate(country_name, point)

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'{stat_type.to_title().title()} (7-day rolling average)')

    ax.xaxis_date()

    # Show the major grid lines with dark grey lines
    plt.grid(zorder=0, b=True, which='major', color='#666666', linestyle='-')

    plt.minorticks_on()
    plt.grid(zorder=0, b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(f'Day\nData updated: {date_update_str}')
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
    y_recovered = []
    for item in country_data:
        cell_value = virus_utils.num(item[stat_type.to_data_name()])
        if cell_value < 1:
            continue

        dt = get_datetime_obj(item)
        x.append(dt)

        # if show_only_weeks is False or dt.weekday() == 0:  # monday only or add all, decrease data
        y.append(cell_value)

        if stat_type == StatType.CONFIRMED:
            val_recovered = virus_utils.num(item[StatType.RECOVERED.to_data_name()])
            y_recovered.append(val_recovered)

    ax.yaxis.set_major_formatter(FuncFormatter(virus_utils.reformat_large_tick_values))

    ax.plot(x, y, marker='', linewidth=2, label=stat_type.to_title().title())  # for each country
    if len(y_recovered) > 0:
        ax.plot(x, y_recovered, marker='', linewidth=2, label=StatType.RECOVERED.to_title().title())  # for each country
        plt.legend(loc="upper left")

    date_update_str = virus_utils.get_formatted_datetime_change_data()
    plt.xlabel(f'Data updated: {date_update_str}')

    ax.set_ylabel(stat_type.to_title().title())
    ax.set_title(f'{country_name} – {stat_type.to_title().title()} Total statistics')

    ax.xaxis_date()
    ax.grid(zorder=0)
    my_fmt = DateFormatter("%b %d")
    ax.xaxis.set_major_formatter(my_fmt)
    fig.autofmt_xdate()  # Rotate date labels automatically

    plt.tight_layout()
    return fig, ax
