import discord
from discord.ext import commands
import asyncio
import time
import datetime
from google_cal_connect import *
import dateutil.parser as parser

description="calendar commands"
bot = commands.Bot(command_prefix='^', description=description)
TOKEN = 'Mzg4MTQyOTA1NjI3MjQ2NjEy.XRrZPg.HN9i3nbzgdDASAPx1M1uOomCWgM'
cal_service = initial_cal()


def time_print(event, service=cal_service):
    """returns time to a future event from the community calendar"""
    out_event = find_event(service, event)
    time_dif = time_to(out_event.time).days
    return f"{time_dif} days til {out_event.summary}"


@bot.event
async def on_ready():



@bot.command()
async def refresh(ctx):
    await ctx.send("refresh")


def main():
    #initialize bot
    bot.run(TOKEN)


main()
