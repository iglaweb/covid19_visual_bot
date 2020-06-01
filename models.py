from collections import namedtuple
from enum import Enum, IntEnum

from dataclasses import dataclass

Country = namedtuple('Country', ['value', 'serverId', 'flag', 'title'])


class Countries(Enum):

    @property
    def displayString(self):
        return f'{self.displayFlag} {self.displayTitle}'

    @property
    def displayValue(self):
        return self.value.value

    @property
    def displayFlag(self):
        return self.value.flag

    @property
    def displayTitle(self):
        return self.value.title

    @property
    def serverId(self):
        return self.value.serverId

    US = Country('US', 'US', '🇺🇸', 'US')  # US - like in stat
    GERMANY = Country('GERMANY', 'Germany', '🇩🇪', 'Germany')
    ITALY = Country('ITALY', 'Italy', '🇮🇹', 'Italy')
    SPAIN = Country('SPAIN', 'Spain', '🇪🇸', 'Spain')
    UK = Country('UK', 'United Kingdom', '🇬🇧', 'United Kingdom')
    BELGIUM = Country('BELGIUM', 'Belgium', '🇧🇪', 'Belgium')
    IRAN = Country('IRAN', 'Iran', '🇮🇷', 'Iran')
    CHINA = Country('CHINA', 'China', '🇨🇳', 'China')
    NL = Country('NL', 'Netherlands', '🇳🇱', 'Netherlands')
    RUSSIA = Country('RUSSIA', 'Russia', '🇷🇺', 'Russia')

    FRANCE = Country('FRANCE', 'France', '🇫🇷', 'France')
    TURKEY = Country('TURKEY', 'Turkey', '🇫🇷', 'Turkey')

    BRAZIL = Country('BRAZIL', 'Brazil', '🇧🇷', 'Brazil')
    CANADA = Country('CANADA', 'Canada', '🇨🇦', 'Canada')

    SWITZERLAND = Country('SWITZERLAND', 'Switzerland', '🇨🇭', 'Switzerland')
    INDIA = Country('INDIA', 'India', '🇮🇳', 'India')

    PERU = Country('PERU', 'Peru', '🇵🇪', 'Peru')
    PORTUGAL = Country('PORTUGAL', 'Portugal', '🇵🇹', 'Portugal')
    ECUADOR = Country('ECUADOR', 'Ecuador', '🇪🇨', 'Ecuador')
    SAUDIARABIA = Country('SAUDIARABIA', 'Saudi Arabia', '🇸🇦', 'Saudi Arabia')

    SWEDEN = Country('SWEDEN', 'Sweden', '🇸🇪', 'Sweden')
    IRELAND = Country('IRELAND', 'Ireland', '🇮🇪', 'Ireland')
    MEXICO = Country('MEXICO', 'Mexico', '🇲🇽', 'Mexico')
    PAKISTAN = Country('PAKISTAN', '🇵🇰', '🇮🇳', 'Pakistan')

    SINGAPORE = Country('SINGAPORE', 'Singapore', '🇸🇬', 'Singapore')
    CHILE = Country('CHILE', 'Chile', '🇨🇱', 'Chile')
    ISRAEL = Country('ISRAEL', 'Israel', '🇮🇪', 'Israel')
    AUSTRIA = Country('AUSTRIA', 'Austria', '🇦🇹', 'Austria')


class StatType(IntEnum):
    DEATHS = 0,
    RECOVERED = 1,
    CONFIRMED = 2

    def to_data_name(self):
        return STAT_TYPES[self.value]['format']

    def to_title(self):
        return STAT_TYPES[self.value]['title']


STAT_TYPES = {
    StatType.DEATHS: {'format': 'deaths', 'title': 'fatal'},
    StatType.RECOVERED: {'format': 'recovered', 'title': 'recovered'},
    StatType.CONFIRMED: {'format': 'confirmed', 'title': 'cases'}
}


class GraphType(IntEnum):
    DEATHS_TOTAL = 0,
    RECOVERED_TOTAL = 1,
    CONFIRMED_TOTAL = 2,

    DEATHS_BAR = 3,
    RECOVERED_BAR = 4,
    CONFIRMED_BAR = 5,

    DEATHS_WEEK = 6,
    RECOVERED_WEEK = 7,
    CONFIRMED_WEEK = 8,

    DEATHS_ACTIVE = 9,
    RECOVERED_ACTIVE = 10,
    CONFIRMED_ACTIVE = 11,

    CONFIRMED_1M_PEOPLE = 12,
    DEATHS_RATE = 13

    def to_name(self) -> str:
        return GRAPH_TYPES[self.value]


GRAPH_TYPES = {
    GraphType.DEATHS_TOTAL: 'deaths_total',
    GraphType.RECOVERED_TOTAL: 'recovered_total',
    GraphType.CONFIRMED_TOTAL: 'confirmed_total',

    GraphType.DEATHS_ACTIVE: 'deaths_active',
    GraphType.RECOVERED_ACTIVE: 'recovered_active',
    GraphType.CONFIRMED_ACTIVE: 'confirmed_active',

    GraphType.DEATHS_WEEK: 'deaths_week',
    GraphType.RECOVERED_WEEK: 'recovered_week',
    GraphType.CONFIRMED_WEEK: 'confirmed_week',

    GraphType.DEATHS_BAR: 'deaths_bar',
    GraphType.RECOVERED_BAR: 'recovered_bar',
    GraphType.CONFIRMED_BAR: 'confirmed_bar',

    GraphType.CONFIRMED_1M_PEOPLE: 'confirmed_1m_people',
    GraphType.DEATHS_RATE: 'deaths_rate'
}


@dataclass
class TimeSeriesItem:
    """Class for keeping track of an item in inventory."""
    country: str
    region: str
    dates: dict
    total: int

    def get_location_name(self) -> str:
        return self.region if not self.country else self.country