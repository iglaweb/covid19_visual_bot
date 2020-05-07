# -*- coding: utf-8 -*-
import json
from datetime import datetime
from enum import Enum

from dataclasses import dataclass


class JsonSerializable(object):
    def toJson(self):
        return json.dumps(self.__dict__, sort_keys=True, default=str)

    def __repr__(self):
        return self.toJson()


@dataclass
class TimeSeriesItem:
    """Class for keeping track of an item in inventory."""
    country: str
    region: str
    dates: dict
    total: int

    def get_location_name(self) -> str:
        return self.region if not self.country else self.country


class VirusData(JsonSerializable):
    total_stats_confirmed: int
    total_stats_cases: int
    date: datetime
    data_list: list

    def __init__(
            self,
            total_stats_confirmed: int,
            total_stats_cases: int,
            date: datetime,
            data_list: list
    ) -> None:
        self.total_stats_confirmed = total_stats_confirmed
        self.total_stats_cases = total_stats_cases
        self.date = date
        self.data_list = data_list


class Region(Enum):
    America = 1
    Asia = 2
    Europe = 3
    Oceania = 4
    Africa = 5
    Other = 6


class StatsData(JsonSerializable):

    def __init__(self, region, area, confirmed, cases):
        """Constructor"""
        self.region = region
        self.area = area
        self.confirmed = confirmed
        self.cases = cases

    def __str__(self):
        return ','.join([self.region.name, self.area, self.confirmed, self.cases])

    def get_list(self):
        return [self.region.name, self.area, self.confirmed, self.cases]
