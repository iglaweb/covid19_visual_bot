import os

from models import GraphType, GRAPH_TYPES, Country


def is_local_run() -> bool:
    host_name = os.uname().nodename
    return 'MacBook-Air.local' in host_name


global dir_path
dir_path = '' if is_local_run() else '/tmp/'  # for Now
print(dir_path)


def create_prefs_dictionary(filename):
    prefs_dict = {}
    with open(filename) as file:
        for line in file:
            k, v = line.rstrip().split('=')
            prefs_dict[k] = v
    return prefs_dict


def get_photo_path_world(graph_type: GraphType) -> str:
    str_title = GRAPH_TYPES[graph_type]
    return f'{dir_path}{str_title}_world.png'


def get_photo_path_country(graph_type: GraphType, country_name: str) -> str:
    str_title = GRAPH_TYPES[graph_type]
    return f'{dir_path}{str_title}_location_{country_name}.png'


def get_photo_path_url(graph_type: GraphType, country: Country = None) -> str:
    if country is None:
        return get_photo_path_world(graph_type)
    else:
        return get_photo_path_country(graph_type, country.value)


def get_data_path() -> str:
    return f'{dir_path}timeseries_data.txt'


def get_prefs_path() -> str:
    return f'{dir_path}settings.txt'
