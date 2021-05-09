import aiohttp
import asyncio
import random
import pickle
import os.path

from Cache import CharCache
from operator import itemgetter
from openpyxl import load_workbook
from dateutil import parser
from datetime import datetime
from datetime import timedelta
from pytz import timezone


class D2Profile:
    """
    object that contains a users user_id, character_ids, and console_stats
    """
    def __init__(self):
        self.title = None
        self.user_id = None
        self.char_ids = None
        self.console = None

reset_time_hours = 17
bung_url = 'https://www.bungie.net/Platform'
baseurl = 'https://bungie.net/Platform/Destiny2/'
baseurl_groupv2 = 'https://bungie.net/Platform/GroupV2/'

my_api_key = '251bdc1107ac4b4e8713b3fd0aea1257'
my_headers = {"X-API-Key": my_api_key}
membership_types = {'xbox': '1',  'xbone': '1', 'psn': '2', 'steam': '3', 'ps4': '2', 'all': '-1', 'blizzard': '4',
                    'demon': '10', 'next': '254', 'stadia': '5'}
seasons = \
    {'S7': ["2019-06-04T17:00:00Z", "2019-10-01T17:00:00Z"], 'S6': ["2019-03-05T17:00:00Z", "2019-06-04T17:00:00Z"],
     'S8': ["2019-10-01T17:00:00Z", "2019-12-010T17:00:00Z"], 'S9': ["2019-12-10T17:00:00Z", "2020-03-09T17:00:00Z"],
     'S10': ["2020-03-09T17:00:00Z", "2020-06-09T17:00:00Z"], 'S11': ["2020-06-09T17:00:00Z", "2020-11-10T17:00:00Z"],
     'S12': ["2020-11-10T17:00:00Z", "2021-03-10T17:00:00Z"], 'S13': ["2021-03-10T17:00:00Z", "2021-05-11T17:00:00Z"],
     'S14': ["2021-05-11T17:00:00Z", "2021-08-11T17:00:00Z"]}
current_season = 'S14'
game_types = { 74:'Control', 72:'Clash', 37:'Survival', 38:'Countdown'}
trials_game_type = {84:'Elimination'}

#D2Profiles = CharCache()
D2Stats = CharCache()


def load_profiles():
    """returns  in d2 character profiles from a pickled file"""
    Profiles = None
    if os.path.exists('d2CharCache.pickle'):
        with open('d2CharCache.pickle', 'rb') as Char_file:
            Profiles = pickle.load(Char_file)
    if not Profiles:
        Profiles = CharCache()
        with open('d2CharCache.pickle', 'wb') as char_file:
            pickle.dump(Profiles, char_file)
    return Profiles

D2Profiles = load_profiles()

async def fetch(session, url):
    async with session.request('GET',url,headers=my_headers) as response:
        return await response.json()



async def get_characters(session, membership_id, console):
    """return a list of int64 id player characters"""

    membershipType = membership_types[console]

    destinyMembershipId = membership_id
    url = bung_url + f"/Destiny2/{membershipType}/Profile/{destinyMembershipId}/?components=100"

    response = await fetch(session, url)
    print(response)
    characters = response['Response']['profile']['data']['characterIds']
    return characters


async def return_member_id(session, name, console):
    """returns user id from input string"""
    membershipType = membership_types["steam"]
    #membershipType = membership_types[console]

    print(name)
    url = bung_url + f"/Destiny2/SearchDestinyPlayer/{membershipType}/{name}/"
    print(url)
    response = await fetch(session, url)
    print(response)
    print(response['Response'][0]['membershipId'])
    return response['Response'][0]['membershipId']


async def return_member_id_from_code(session, credential, console):

    membershipType = membership_types[console]

    crType = 'SteamId'
    url = bung_url + f"/User/GetMembershipFromHardLinkedCredential/{crType}/{credential}/"
    print(url)
    response = await fetch(session, url)

    return response['Response']['membershipId']


async def register(title, steamID):
    """
    connects a users name and steam id and create a profile for a user
    """
    async with aiohttp.ClientSession() as session:
        console = "steam"
        profile = D2Profile()
        profile.user_id = await return_member_id_from_code(session, steamID, console)
        profile.char_ids = await get_characters(session, profile.user_id, console)
        profile.console = console
        key = title + console
        D2Profiles.update(key, profile)
        with open('d2CharCache.pickle', 'wb') as char_file:
            pickle.dump(D2Profiles, char_file)
        print("registration complete")
        if key in D2Profiles.cache:
            print("registration success")
            error = 1
        else:
            print("registration failure")
            error = 0
        return error


async def find_profile(session, name, console):
    """
    Searches a cache for name if in cache return user_id char_id, and char_platform if not in cache search destiny
    api for same information
    """
    key = name + console
    if key in D2Profiles.cache:
        print("user in cache")
        return D2Profiles.cache[key]['value']
    else:
        profile = D2Profile()
        # checks if steamid or user name
        if name[0].isdigit():
            profile.user_id = await return_member_id_from_code(session, name, console)
        else:
            profile.user_id = await return_member_id(session, name, console)

        profile.char_ids = await get_characters(session, profile.user_id, console)
        profile.console = console
        D2Profiles.update(key, profile)
        with open('d2CharCache.pickle', 'wb') as char_file:
            pickle.dump(D2Profiles, char_file)
        print("user added from Bungie API")
        return profile


async def get_historical_activitys(session,destinyMembershipId,console,characterId,count,page = '0',mode = '0'):
    """gets historical stats for daystart to dayend"""
    membershipType = membership_types[console]
    url = bung_url + f'/Destiny2/{membershipType}/Account/{destinyMembershipId}/Character/{characterId}/Stats/Activities/' \
    + f'?count={count}&mode={mode}&page={page}'
    print(url)

    response = await fetch(session, url)

    return response['Response']


def find_scope_time(season=None,week=None):

    if season is None:
        if week is None:
            if datetime.utcnow().hour > reset_time_hours:
                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)-timedelta(days=1)
        else:
            today = parser.parse(week)

        if today.weekday() == 1:
            offset = 0
        else:
            offset = (today.weekday() - 1) % 7

        reset = today - timedelta(days=offset) + timedelta(hours=reset_time_hours)
        reset_next = reset + timedelta(days=7)

        search_on = {'start':str(reset.isoformat() + "Z"),'stop':str(reset_next.isoformat() + "Z")}

    season_times = seasons[season]
    search_on = {'start': season_times[0], 'stop': season_times[1]}

    return search_on


async def build_banner(session, name, console, start_search_on, stop_search_on):

    profile = await find_profile(session, name, console)
    win_list = []
    for character in profile.char_ids:
        page = 0
        try:
            stats = await get_historical_activitys(session, profile.user_id, console, character, '5', '0', '19')
            print(stats)
            while 'activities' in stats and stats['activities'][0]['period'] > start_search_on:
                page = page + 1
                num = 0
                while num < 5 and stats['activities'][num]['period'] > start_search_on and stats['activities'][num]['period'] < stop_search_on:
                    win_dict = {}
                    win_dict['period'] = stats['activities'][num]['period']
                    win_dict['win/loss'] = stats['activities'][num]['values']['standing']['basic']['displayValue']
                    win_dict['kills'] = stats['activities'][num]['values']['kills']['basic']['value']
                    win_dict['assists'] = stats['activities'][num]['values']['assists']['basic']['value']
                    win_dict['deaths'] = stats['activities'][num]['values']['deaths']['basic']['value']
                    win_dict['mode'] = stats['activities'][num]['activityDetails']['mode']
                    win_dict['duration'] = stats['activities'][num]['values']['activityDurationSeconds']['basic']['value']
                    win_list.append(win_dict)
                    print(win_dict)
                    num = num + 1
                stats = await get_historical_activitys(session, profile.user_id, console, character, '5', str(page), '19')

        except TypeError:
            print("banner history does not exist for this character")

    return sorted(win_list, key=itemgetter('period'))


def pushto_excel_banner(banner_build, time_start, time_stop, savename, tz):
    """push win and loss data to excel sheet"""
    time_start = parser.parse(time_start).astimezone(timezone(tz))
    time_stop = parser.parse(time_stop).astimezone(timezone(tz))
    wb = load_workbook(filename='banner_base.xlsx')
    ws = wb.active
    ws['B2'] = time_start.date()
    ws['B3'] = time_stop.date()
    game_col = 6
    for game in banner_build:
        ws['A'+str(game_col)] = game_col - 5
        game_date = parser.parse(game['period']).astimezone(timezone(tz))

        if game['win/loss'] == "Victory":
            ws['B'+str(game_col)] = "W"
        else:
            ws['B' + str(game_col)] = "L"

        ws['C' + str(game_col)] = game['kills']
        ws['D' + str(game_col)] = game['assists']
        ws['E' + str(game_col)] = game['deaths']
        ws['H' + str(game_col)] = game_date.date()
        ws['I' + str(game_col)] = game_date.time()
        ws['N' + str(game_col)] = game['duration']
        game_col = game_col+1

    filename = f'{time_start.strftime("%m_%d_%y")}banner_{savename}.xlsx'
    wb.save(filename)
    return filename


async def banner_stats(name, console="pc", season=None, week=None, tz="US/Pacific"):
    async with aiohttp.ClientSession() as session:
        time = find_scope_time(season,week)
        build = await build_banner(session, name, console, time['start'], time['stop'])
        return pushto_excel_banner(build, time['start'], time['stop'], name, tz)


async def build_trials(session, name, console, start_search_on, stop_search_on):

    profile = await find_profile(session, name, console)
    win_list = []
    for character in profile.char_ids:
        page = 0
        try:
            stats = await get_historical_activitys(session, profile.user_id, console, character, '5', '0', '84')
            print(stats)
            while 'activities' in stats and stats['activities'][0]['period'] > start_search_on:
                page = page + 1
                num = 0
                next_time = stats['activities'][num]['period']
                while num < 5 and next_time > start_search_on and stats['activities'][num]['period'] < stop_search_on:
                    win_dict = {}
                    win_dict['period'] = stats['activities'][num]['period']
                    win_dict['win/loss'] = stats['activities'][num]['values']['standing']['basic']['displayValue']
                    win_dict['kills'] = stats['activities'][num]['values']['kills']['basic']['value']
                    win_dict['assists'] = stats['activities'][num]['values']['assists']['basic']['value']
                    win_dict['deaths'] = stats['activities'][num]['values']['deaths']['basic']['value']
                    win_dict['mode'] = stats['activities'][num]['activityDetails']['mode']
                    win_dict['duration'] = stats['activities'][num]['values']['activityDurationSeconds']['basic']['value']
                    win_list.append(win_dict)
                    print(win_dict)
                    num = num + 1
                    try:
                        next_time = stats['activities'][num]['period']
                    except IndexError:
                        next_time = 0
                        print("end of games")

                stats = await get_historical_activitys(session, profile.user_id, console, character, '5', str(page), '84')

        except TypeError:
            print("trials history does not exist for this character")

    return sorted(win_list, key=itemgetter('period'))


def pushto_excel_trials(trials_build, time_start, time_stop, savename, tz):
    """push win and loss data to excel sheet"""
    time_start = parser.parse(time_start).astimezone(timezone(tz))
    time_stop = parser.parse(time_stop).astimezone(timezone(tz))
    wb = load_workbook(filename='trials_base.xlsx')
    ws = wb.active
    ws['B2'] = time_start.date()
    ws['B3'] = time_stop.date()
    game_col = 6
    for game in trials_build:
        ws['A'+str(game_col)] = game_col - 5
        game_date = parser.parse(game['period']).astimezone(timezone(tz))

        if game['win/loss'] == "Victory":
            ws['B'+str(game_col)] = "W"
        else:
            ws['B' + str(game_col)] = "L"

        ws['C' + str(game_col)] = game['kills']
        ws['D' + str(game_col)] = game['assists']
        ws['E' + str(game_col)] = game['deaths']
        ws['H' + str(game_col)] = game_date.date()
        ws['I' + str(game_col)] = game_date.time()
        ws['N' + str(game_col)] = game['duration']
        game_col = game_col+1

    filename = f'{time_start.strftime("%m_%d_%y")}trials_{savename}.xlsx'
    wb.save(filename)
    return filename


async def trials_stats(name, console="pc", season=None, week=None, tz="US/Pacific"):
    async with aiohttp.ClientSession() as session:
        time = find_scope_time(season,week)
        build = await build_trials(session, name, console, time['start'], time['stop'])
        return pushto_excel_trials(build, time['start'], time['stop'], name, tz)


async def build_comp(session, name, console, season):
    """returns stats in a list for comp in a season"""

    season_times = seasons[season]
    season_start = season_times[0]
    season_end = season_times[1]

    profile = await find_profile(session, name, console)
    win_list = []
    for character in profile.char_ids:
        page = 0
        try:
            stats = await get_historical_activitys(session, profile.user_id, console, character, '5', '0', '69')
            while 'activities' in stats and stats['activities'][0]['period'] > season_start:
                page = page + 1
                num = 0
                while num < 5 and stats['activities'][num]['period'] > season_start and stats['activities'][num]['period'] < season_end:
                    win_dict = {}
                    win_dict['period'] = stats['activities'][num]['period']
                    win_dict['win/loss'] = stats['activities'][num]['values']['standing']['basic']['displayValue']
                    win_dict['kills'] = stats['activities'][num]['values']['kills']['basic']['value']
                    win_dict['assists'] = stats['activities'][num]['values']['assists']['basic']['value']
                    win_dict['deaths'] = stats['activities'][num]['values']['deaths']['basic']['value']
                    win_dict['mode'] = stats['activities'][num]['activityDetails']['mode']
                    win_list.append(win_dict)
                    print(win_dict)
                    num = num + 1
                stats = await get_historical_activitys(session, profile.user_id, console, character, '5', str(page), '69')
        except TypeError:
            print("comp history does not exist for this character")

    return sorted(win_list, key=itemgetter('period'))


def pushto_excel_comp(comp_build, season, savename, tz):
    """push win and loss data to excel sheet"""

    season_times = seasons[season]
    season_start = season_times[0]
    season_end = season_times[1]

    season_start_date = parser.parse(season_start).astimezone(timezone(tz))
    season_end_date = parser.parse(season_end).astimezone(timezone(tz))
    next_reset = season_start_date + timedelta(days=7)
    print(next_reset)

    wb = load_workbook(filename='glory_base.xlsx')
    ws = wb.active
    ws['G22'] = season_start_date.date()
    ws['H22'] = season_end_date.date()
    col = 32
    game_col = 32
    for game in comp_build:
        ws['R'+str(game_col)] = game_col - 31
        current_cell = 'O' + str(col)
        print(current_cell)
        game_date = parser.parse(game['period']).astimezone(timezone(tz))
        while game_date > next_reset:
            ws[current_cell] = "G"
            col = col + 1
            current_cell = 'O' + str(col)
            next_reset = next_reset + timedelta(days=7)
        if game['win/loss'] == "Victory":
            ws[current_cell] = "W"
            ws['S'+str(game_col)] = "W"
        else:
            ws[current_cell] = "L"
            ws['S' + str(game_col)] = "L"
        ws['T' + str(game_col)] = game['kills']
        ws['U' + str(game_col)] = game['assists']
        ws['V' + str(game_col)] = game['deaths']
        try:
            ws['AA' + str(game_col)] = game_types[game['mode']]
        except KeyError:
            ws['AA' + str(game_col)] = game['mode']
        ws['W' + str(game_col)] = game_date.date()
        ws['X' + str(game_col)] = game_date.time()
        col = col + 1
        game_col = game_col+1
    filename = f'{season}glory_{savename}.xlsx'
    print(filename)
    wb.save(filename)
    return filename


async def competitive_stats(name,console,season):
    async with aiohttp.ClientSession() as session:
        return await build_comp(session,name,console,season)


async def get_stats(session, user_id, console):
    """gets overall stats for character"""
    membershipType = membership_types[console]
    destinyMembershipId = user_id
    url = bung_url + f"/Destiny2/{membershipType}/Account/{destinyMembershipId}/Stats/"
    print(url)

    response = await fetch(session, url)
    return response['Response']


async def find_stats(session, profile, console):
    """gets overall stats from cache or api"""

    key = profile.user_id + console
    if key in D2Stats.cache and D2Stats.cache[key]['date_accessed'] > datetime.now() - timedelta(days=1):
        print(D2Stats.cache[key]['date_accessed'])
        print("stats in cache")
        return D2Stats.cache[key]['value']
    else:
        stat = await get_stats(session, profile.user_id, console)
        D2Stats.update(key, stat)
        print("stats added from Bungie API")
        return stat


def cut_stat_key(key):
    key = key[:1].upper() + key[1:]
    pos = [i for i, e in enumerate(key + 'A') if e.isupper()]
    parts = [key[pos[j]:pos[j + 1]] for j in range(len(pos) - 1)]
    return parts


def remove_hashtag(name):
    return name.split("#")[0]


async def fight_stats(player_1,player_2,console):
    async with aiohttp.ClientSession() as session:
        if console == "pc":
            name_1 = remove_hashtag(player_1)
            name_2 = remove_hashtag(player_2)
        else:
            name_1 = player_1
            name_2 = player_2

        profile_1 = await find_profile(session, player_1, console)

        stats_1 = await find_stats(session, profile_1, console)

        enemy_type = random.choice(['allPvP', 'allPvE'])
        dict_1 = stats_1["mergedAllCharacters"]['results'][enemy_type]['allTime']

        random_key = random.sample(list(dict_1), 1)[0]
        print(random_key)
        cut_key = cut_stat_key(random_key)

        profile_2 = await find_profile(session, player_2, console)

        stats_2 = await find_stats(session, profile_2, console)
        dict_2 = stats_2["mergedAllCharacters"]['results'][enemy_type]['allTime']

        value_1 = dict_1[random_key]["basic"]["value"]
        value_2 = dict_2[random_key]["basic"]["value"]
        val_dif = abs(value_1-value_2)
        if val_dif > 10:
            val_dif = "{:,.0f}".format(val_dif)
        else:
            val_dif = "{:,.2f}".format(val_dif)

        if value_1 > value_2:
            s = f"{name_1} has {val_dif} more"
            for word in cut_key:
                s = s + f" {word.lower()}"
            s = s + f" than {name_2}"
        elif value_2 > value_1:
            s = f"{name_2} has {val_dif} more"
            for word in cut_key:
                s = s + f" {word.lower()}"
            s = s + f" than {name_1}"
        else:
            s = f"Both players have {value_1}"
            for word in cut_key:
                s = s + f" {word.lower()}"
        s = s + f" in {enemy_type[3:]}"
        return s


async def example():
    #test = await banner_stats("Brytron","steam",season="S11")

    async with aiohttp.ClientSession() as session:
        membershipType = membership_types['stadia']
        # membershipType = membership_types[console]
        name = 'Bryton'
        url = bung_url + f"/Destiny2/SearchDestinyPlayer/{membershipType}/{name}/"
        print(url)
        response = await fetch(session, url)
        print(response)
        print(response['Response'][0]['membershipId'])



#loop = asyncio.get_event_loop()
#loop.run_until_complete(example())

