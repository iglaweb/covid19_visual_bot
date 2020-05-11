import csv
import os
from typing import Dict, Any

import virus_utils
from models import GraphType, GRAPH_TYPES, Country

# taken from https://www.kaggle.com/tanuprabhu/population-by-country-2020
country_population_str = """China,1438207241
India,1377233523
United States,330610570
Indonesia,272931713
Pakistan,219992900
Brazil,212253150
Nigeria,205052107
Bangladesh,164354176
Russia,145922010
Mexico,128655589
Japan,126552765
Ethiopia,114357494
Philippines,109280343
Egypt,101930276
Vietnam,97160127
DR Congo,88972681
Turkey,84153250
Iran,83771587
Germany,83730223
Thailand,69764925
United Kingdom,67814098
France,65244628
Italy,60479424
Tanzania,59368313
South Africa,59154802
Myanmar,54335948
Kenya,53521116
South Korea,51260395
Colombia,50771878
Spain,46751175
Uganda,45427637
Argentina,45111229
Algeria,43685618
Sudan,43632213
Ukraine,43785122
Iraq,40031626
Afghanistan,38742911
Poland,37854825
Canada,37674770
Morocco,36820713
Saudi Arabia,34701377
Uzbekistan,33368859
Peru,32876986
Angola,32644783
Malaysia,32280610
Mozambique,31067362
Ghana,30936375
Yemen,29687214
Nepal,29027347
Venezuela,28451828
Madagascar,27539106
Cameroon,26405174
C̫te d'Ivoire,26239250
North Korea,25756088
Australia,25439164
Niger,24014064
Taiwan,23808164
Sri Lanka,21395196
Burkina Faso,20780371
Mali,20125282
Romania,19262731
Malawi,19024426
Chile,19082804
Kazakhstan,18730568
Zambia,18273379
Guatemala,17846248
Ecuador,17587526
Syria,17410293
Netherlands,17127290
Senegal,16649599
Cambodia,16671185
Chad,16324440
Somalia,15798020
Zimbabwe,14818157
Guinea,13056478
Rwanda,12883878
Benin,12055347
Burundi,11814346
Tunisia,11793319
Bolivia,11640159
Belgium,11579477
Haiti,11373955
Cuba,11327988
South Sudan,11166783
Dominican Republic,10825682
Czech Republic (Czechia),10705012
Greece,10433037
Jordan,10182442
Portugal,10202571
Azerbaijan,10120555
Sweden,10086531
Honduras,9871892
United Arab Emirates,9865845
Hungary,9665192
Tajikistan,9492342
Belarus,9449940
Austria,8996022
Papua New Guinea,8911530
Serbia,8744288
Israel,8627444
Switzerland,8641786
Togo,8237580
Sierra Leone,7942879
Hong Kong,7484618
Laos,7253719
Paraguay,7114524
Bulgaria,6958627
Libya,6852010
Lebanon,6831445
Nicaragua,6608366
Kyrgyzstan,6501804
El Salvador,6479609
Turkmenistan,6012850
Singapore,5840996
Denmark,5788108
Finland,5539002
Congo,5489191
Slovakia,5459116
Norway,5412632
Oman,5078933
State of Palestine,5076280
Costa Rica,5084636
Liberia,5032469
Ireland,4926480
Central African Republic,4812256
New Zealand,4814272
Mauritania,4623535
Panama,4300667
Kuwait,4257495
Croatia,4110214
Moldova,4035814
Georgia,3990681
Eritrea,3536285
Uruguay,3471314
Bosnia and Herzegovina,3284806
Mongolia,3267320
Armenia,2962137
Jamaica,2958567
Qatar,2870922
Albania,2878420
Puerto Rico,2874636
Lithuania,2729553
Namibia,2531290
Gambia,2402083
Botswana,2341649
Gabon,2214593
Lesotho,2138799
North Macedonia,2083391
Slovenia,2078881
Guinea-Bissau,1958132
Latvia,1890218
Bahrain,1688629
Equatorial Guinea,1392950
Trinidad and Tobago,1398579
Estonia,1326357
Timor-Leste,1313184
Mauritius,1271347
Cyprus,1205577
Eswatini,1157707
Djibouti,985027
Fiji,895128
R̩union,894017
Comoros,865696
Guyana,785788
Bhutan,769867
Solomon Islands,683301
Macao,647508
Montenegro,628050
Luxembourg,623861
Western Sahara,594215
Suriname,585561
Cabo Verde,554750
Maldives,538558
Malta,441308
Brunei,436624
Guadeloupe,400110
Belize,396120
Bahamas,392477
Martinique,375323
Iceland,340795
Vanuatu,305623
French Guiana,297029
Barbados,287305
New Caledonia,284938
French Polynesia,280580
Mayotte,271417
Sao Tome & Principe,218308
Samoa,198147
Saint Lucia,183458
Channel Islands,173536
Guam,168474
Cura̤ao,163958
Kiribati,119069
Micronesia,114776
Grenada,112418
St. Vincent & Grenadines,110869
Aruba,106675
Tonga,105449
U.S. Virgin Islands,104456
Seychelles,98224
Antigua and Barbuda,97764
Isle of Man,84942
Andorra,77240
Dominica,71950
Cayman Islands,65564
Bermuda,62323
Marshall Islands,59109
Northern Mariana Islands,57490
Greenland,56750
American Samoa,55215
Saint Kitts & Nevis,53123
Faeroe Islands,48826
Sint Maarten,42776
Monaco,39186
Turks and Caicos,38609
Saint Martin,38529
Liechtenstein,38106
San Marino,33917
Gibraltar,33693
British Virgin Islands,30190
Caribbean Netherlands,26173
Palau,18077
Cook Islands,17561
Anguilla,14976
Tuvalu,11762
Wallis & Futuna,11276
Nauru,10810
Saint Barthelemy,9871
Saint Helena,6073
Saint Pierre & Miquelon,5800
Montserrat,4991
Falkland Islands,3458
Niue,1624
Tokelau,1354
Holy See,801"""


def is_local_run() -> bool:
    host_name = os.uname().nodename
    return 'MacBook-Air.local' in host_name


global dir_path
dir_path = '' if is_local_run() else '/tmp/'  # for Zeit Now
print(dir_path)


def read_country_population() -> Dict[str, Any]:
    country_population = {}
    lines = country_population_str.splitlines()
    reader = csv.reader(lines, delimiter=',')
    for line in reader:
        country_name = line[0].lower()
        country_population[country_name] = virus_utils.num(line[1])
    return country_population


# lowercase country names
population = read_country_population()


def get_population(country_server_name: str) -> int:
    country_server_name = country_server_name.lower()
    if country_server_name == 'us' or country_server_name == 'united states':
        return population['united states']

    country = population.get(country_server_name)
    if country is None:
        return 0
    return country


def create_prefs_dictionary(filename) -> dict:
    prefs_dict = {}
    with open(filename) as file:
        for line in file:
            k, v = line.rstrip().split('=')
            prefs_dict[k] = v
    return prefs_dict


def read_system_credentials():
    prefs = create_prefs_dictionary('.prefs')
    if bool(prefs) is False:
        print('Cannot continue. System credentials are not set up')
        return

    token_prod = prefs['token_prod']
    token_debug = prefs['token_debug']
    webhook_url = prefs['webhook_url']
    token = token_debug \
        if is_local_run() \
        else token_prod
    return token, webhook_url


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
