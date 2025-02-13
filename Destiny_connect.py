import aiohttp
import pickle
import os.path
import json
from Cache import CharCache



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

with open("config.json", "r") as f:
    my_api_key = json.load(f)["Destiny"]["APICode"]

my_headers = {"X-API-Key": my_api_key}
membership_types = {'xbox': '1',  'xbone': '1', 'psn': '2', 'steam': '3', 'ps4': '2', 'all': '-1', 'blizzard': '4',
                    'demon': '10', 'next': '254'}
seasons = \
    {'S7': ["2019-06-04T17:00:00Z", "2019-10-01T17:00:00Z"], 'S6': ["2019-03-05T17:00:00Z", "2019-06-04T17:00:00Z"],
     'S8': ["2019-10-01T17:00:00Z", "2019-12-010T17:00:00Z"], 'S9': ["2019-12-10T17:00:00Z", "2020-03-09T17:00:00Z"],
     'S10': ["2020-03-09T17:00:00Z", "2020-06-09T17:00:00Z"], 'S11': ["2020-06-09T17:00:00Z", "2020-11-10T17:00:00Z"],
     'S12': ["2020-11-10T17:00:00Z", "2021-03-10T17:00:00Z"], 'S13': ["2021-03-10T17:00:00Z", "2021-05-11T17:00:00Z"],
     'S14': ["2021-05-11T17:00:00Z", "2021-08-11T17:00:00Z"], 'S15': ["2021-08-24T17:00:00Z", "2022-02-22T17:00:00Z"],
     'S16': ["2022-02-22T17:00:00Z", "2022-05-24T17:00:00Z"], 'S17': ["2022-05-24T17:00:00Z", "2022-08-23T17:00:00Z"],
     'S18': ["2022-08-23T17:00:00Z", "2022-12-06T17:00:00Z"], 'S19': ["2022-12-06T17:00:00Z", "2023-02-28T17:00:00Z"],
     'S20': ["2023-02-28T17:00:00Z", "2023-05-21T17:00:00Z"], 'S21': ["2023-05-21T17:00:00Z", "2023-08-22T17:00:00Z"],
     'S22': ["2023-08-22T17:00:00Z", "2023-11-28T17:00:00Z"], 'S23': ["2023-11-28T17:00:00Z", "2024-06-04T17:00:00Z"],
     'S24': ["2024-06-04T17:00:00Z", "2024-10-08T17:00:00Z"], 'S25': ["2024-10-08T17:00:00Z", "2025-02-04T17:00:00Z"],
     'S26': ["2025-02-04T17:00:00Z", "2025-06-15T17:00:00Z"]}
current_season = 'S26'
game_types = { 74:'Control', 72:'Clash', 37:'Survival', 38:'Countdown'}
trials_game_type = {84:'Elimination'}

#D2Profiles = CharCache()
D2Stats = CharCache()


def replace_hash(name_in):
    "replaces the '#' in user_input of bungie names"
    name_api = name_in.replace("#", "%23")
    return name_api


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
    print(membershipType)
    destinyMembershipId = membership_id
    url = bung_url + f"/Destiny2/{membershipType}/Profile/{destinyMembershipId}/?components=100"

    response = await fetch(session, url)
    print(response)
    characters = response['Response']['profile']['data']['characterIds']
    return characters


async def return_member_id(session, name, console):
    """returns user id from input string"""
    search_membershipType = membership_types["all"]
    user_selected_membershipType = membership_types[console]

    print(name)
    name = replace_hash(name)
    url = bung_url + f"/Destiny2/SearchDestinyPlayer/{search_membershipType}/{name}/"
    print(url)
    response = await fetch(session, url)
    membership_id = None
    for item in response['Response']:
        print(item)
        print(user_selected_membershipType)
        print(item['applicableMembershipTypes'])
        print(item['membershipId'])
        for i in item['applicableMembershipTypes']:
            if str(i) == str(user_selected_membershipType):
                print('member id found')
                return item['membershipId']

    return membership_id


async def return_member_id_from_code(session, credential, console):
    """returns an id from a steam code, this can probably be removed at some point"""
    membershipType = membership_types[console]

    crType = 'SteamId'
    url = bung_url + f"/User/GetMembershipFromHardLinkedCredential/{crType}/{credential}/"
    print(url)
    response = await fetch(session, url)

    return response['Response']['membershipId']


async def register(title, bungieID, console):
    """
    connects a users name and bungieID and creates a profile for a user
    """
    async with aiohttp.ClientSession() as session:
        profile = D2Profile()
        profile.user_id = await return_member_id(session, bungieID, console)
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
    Searches a cache for name if in cache returns user_id char_id, and char_platform. if not in cache search destiny
    api for same information
    """
    key = name + console
    if key in D2Profiles.cache:
        print("user in cache")
        return D2Profiles.cache[key]['value']
    else:
        profile = D2Profile()
        profile.user_id = await return_member_id(session, name, console)
        profile.char_ids = await get_characters(session, profile.user_id, console)
        profile.console = console
        D2Profiles.update(key, profile)
        with open('d2CharCache.pickle', 'wb') as char_file:
            pickle.dump(D2Profiles, char_file)
        print("user added from Bungie API")
        return profile

