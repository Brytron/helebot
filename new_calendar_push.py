import discord
from discord.ext import commands
import asyncio
import json
import time
import datetime
from google_cal_connect import *
import dateutil.parser as parser

description="calendar commands"
bot = commands.Bot(command_prefix='^', description=description)

with open("config.json", "r") as f:
    TOKEN = json.load(f)["GoogleCal"]["APICode"]

cal_service = initial_cal()


def time_print(event, service=cal_service):
    """returns time to a future event from the community calendar"""
    out_event = find_event(service, event)
    time_dif = time_to(out_event.time).days
    return f"{time_dif} days til {out_event.summary}"

@bot.start
def main():
    channels = bot.get_all_channels()
    channel = next(channels)
    while str(channel) != "calendar" and channel != "None":
        channel = next(channels)
    print(channel)
    while True:
        tracked_event = next_event(cal_service)
        if datetime.datetime.now().minute < 20:
            next_check = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
                minutes=30)
        else:
            next_check = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
                hours=1)
        time_to_event = time_to(tracked_event['start']['dateTime'])
        old_event_str = None
        event_time = parser.parse(tracked_event['start']['dateTime']).replace(tzinfo=None)
        while event_time > datetime.datetime.now() < next_check:
            event_str = f"{tracked_event['summary']} in {time_to_event.days}d{int(time_to_event.seconds/3600)}h"
            game = discord.Game(event_str)
            bot.change_presence(activity=game)
            if event_str != old_event_str:
                channel.send(event_str)
            asyncio.sleep(5)
            time_to_event = time_to(tracked_event['start']['dateTime'])
            old_event_str = event_str

main()