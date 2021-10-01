import discord
from selectimage import *
from Destiny_Stats import *
from pathlib import Path
import asyncio
from google_cal_connect import *
from google_spreedsheet_connect import *
from dateutil import parser
from dateutil.tz import gettz

from discord.ext import commands

#read token
with open("config.json", "r") as f:
    TOKEN = json.load(f)["Discord"]["APICode"]

#version 0.3 (public)

description = '''Helebot version 0.2'''
bot = commands.Bot(command_prefix='*', description=description)

#initialize calendar
cal_service = initial_cal()
drive_service = initial_drive()
current_season = "S15"

pic_path = "wheresRyan_photos/"
Ryan = "Congohunter"
Bryton = "Bryton"
Tyler = "LtDangle"
cal_link = \
    "https://calendar.google.com/calendar?cid=ZGMybmZmbm43NjdiYmt1amdrbjAwOHVzb29AZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ"

countdown_break = False



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


async def print_week(channel):
    await channel.send(pretty_week())


async def print_today(channel, event_list):
    if not event_list:
        await channel.send("No upcoming events in the next week")
    else:
        for event in event_list:
            await channel.send(pretty_event(event))


@bot.command()
@commands.has_permissions(administrator=True)
async def countdown(ctx, event_title, event_date, event_time, event_length=60, event_tz="PST"):
    """
    outputs time to an event in the discord bots status Note: separate from google calendar
    :param ctx: context pass
    :param event_title: Title of Event Note: should be less than 10 characters
    :param event_date: date: suggested format: 01/01/1900
    :param event_time: time of event. suggested format 12:00AM
    :param event_length: length of time of event in minutes. default: 60
    :param event_tz: time zone where the event takes place. Supported timezones PST, MST, CST, and EST. default PST
    :return:
    """
    channel = ctx
    tzinfos = {"PST": gettz("US/Pacific"), "CST": gettz("Central Standard Time"),
               "MST": gettz("Mountain Standard Time"),
               "EST": gettz("Eastern Standard Time")}
    try:
        event_datetime = parser.parse(event_date + " " + event_time + " " + event_tz, tzinfos=tzinfos)
        now_time = datetime.datetime.now().astimezone()
        while event_datetime + datetime.timedelta(minutes=event_length) >= now_time and not countdown_break:
            event_difference = event_datetime - now_time
            if event_datetime < now_time:
                event_str = f"{event_title} is happening now"
            elif event_datetime.date() == now_time.date():
                hours = int(event_difference.seconds / 3600)
                minutes = int(event_difference.seconds / 60) % 60
                event_str = f"{event_title} today in {hours}h {minutes}m"
            else:
                event_str = \
                    f"{event_title} in {event_difference.days}d{int(event_difference.seconds / 3600)}h"
            await asyncio.sleep(20)
            now_time = datetime.datetime.now().astimezone()
            if now_time.minute % 1 == 0:
                game = discord.Game(event_str)
                await bot.change_presence(activity=game)


    except parser._parser.ParserError or OverflowError:
        await ctx.send("Parser failed *help for more info")


@bot.command()
@commands.has_permissions(administrator=True)
async def countdownClear(ctx):
    await ctx.send("Clearing countdown timer")
    global countdown_break
    countdown_break = True
    await asyncio.sleep(40)
    countdown_break = False
    await bot.change_presence()
    await ctx.send("Countdown timer cleared")


@bot.command()
@commands.has_permissions(administrator=True)
async def initialCal(ctx):
    """
    WORK IN PROGRESS
    initializes the calendar for the server
    """
    channel = ctx
    # auto_message loop
    next_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(
        days=1)
    update_day = 0
    last_event_list = None
    while True:
        # send the current calendar information for the week or update if there are changes
        event_list = get_weeks_events(cal_service)
        if update_day == 0:
            await print_week(channel)
            await print_today(channel, event_list)
        elif event_list != last_event_list:
            await print_today(channel, event_list)
        await asyncio.sleep(30)
        while datetime.datetime.now() < next_day:
            # look at upcoming event
            tracked_event = next_event(cal_service)
            # look for next time the calendar should update
            if datetime.datetime.now().minute < 20:
                next_check = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
                    minutes=30)
            else:
                next_check = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(
                    hours=1)
            # find time to next event
            old_event_str = None
            if tracked_event is not None:
                time_to_event = time_to(tracked_event['start']['dateTime'])
                event_time = parser.parse(tracked_event['start']['dateTime']).replace(tzinfo=None)
            while datetime.datetime.now() < next_check:
                if tracked_event is None:
                    event_str = "No Upcoming Events"
                elif event_time > datetime.datetime.now():
                    if event_time.date() == datetime.datetime.now().date():
                        event_str = f"{tracked_event['summary']} today {event_time.hour}h{event_time.minute}m"
                    else:
                        event_str = \
                            f"{tracked_event['summary']} in {time_to_event.days}d{int(time_to_event.seconds/3600)}h"
                else:
                    event_str = f"{tracked_event['summary']} active"
                if event_str != old_event_str:
                    game = discord.Game(event_str)
                    await bot.change_presence(activity=game)
                await asyncio.sleep(60)
                if tracked_event is not None:
                    time_to_event = time_to(tracked_event['start']['dateTime'])
                old_event_str = event_str
            await asyncio.sleep(30)
        next_day = next_day + datetime.timedelta(days=1)
        last_event_list = event_list
        update_day = datetime.datetime.now().weekday()


@bot.command()
async def wheres(ctx, target: discord.Member):
    """mentions a individual member of the guild"""

    try:
        name = target.display_name
        print(target.display_name)
    except:
        await ctx.send("Member can't be found")
        return

    guy = Path(pic_path + f'/Member_photos/{name}.png')

    if name == Bryton:
        vpath = pic_path + '/destiny'
    else:
        vpath = pic_path + '/vistas'

    random_filename = random.choice([
        x for x in os.listdir(vpath)
        if os.path.isfile(os.path.join(vpath, x))
    ])

    vista = Path(vpath + "/" + random_filename)

    out = Path(pic_path+'/outputs/newimage.png')


    try:
        add_ryan(guy, vista, out)
    except FileNotFoundError:
        await ctx.send(target.mention + "can't be found")

    if target.is_on_mobile():
        fence = Path(pic_path + '/creep_asset/Fence.png')
        add_fence(fence, out, out)

    await ctx.send(target.mention,file=discord.File(out))


@bot.command()
async def assemble(ctx, target: discord.Role):
    "mentions a entire role"
    out = Path(pic_path + '/outputs/newimage.png')
    vpath = pic_path + '/vistas'

    random_filename = random.choice([
        x for x in os.listdir(vpath)
        if os.path.isfile(os.path.join(vpath, x))
    ])

    vista = Path(vpath + "/" + random_filename)

    guy1 = Path(pic_path + '/Member_photos/Brytron.png')
    guy2 = Path(pic_path + '/Member_photos/Congohunter.png')
    guy3 = Path(pic_path + '/Member_photos/Jet3010.png')

    add_all(guy1,guy2,guy3,vista,out)

    await ctx.send(target.mention, file=discord.File(out))


@bot.command()
async def talkingstick(ctx, target: discord.Member = ""):
    "unmutes selected member and mutes all others in the channel"
    user = ctx.message.author
    try:
        voice_channel = user.voice.channel
        print(voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return
    if target == "":
        target = user
    for member in voice_channel.members:
        if target == member:
            await member.edit(mute=False)
        else:
            await member.edit(mute=True)


@bot.command()
async def unmute(ctx, target: discord.Member):
    "unmutes a specific member"
    await target.edit(mute=False)


@bot.command()
async def unmuteall(ctx):
    "unmutes all member in the users voice Channel"
    user = ctx.message.author

    try:
        voice_channel = user.voice.channel
        print(voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return

    for member in voice_channel.members:
        await member.edit(mute=False)


@bot.command()
async def pong(ctx,target: discord.Member):
    """mentions a discord member"""
    await ctx.send(target.mention)


@bot.command()
async def comp(ctx, player, season=current_season, console="steam", file_type="sheets", tz="US/Pacific"):
    """builds a excel file(compatible with google sheets) of stats, and progression for a specified season of competitive for an individual destiny player
    Query: comp {player} {season} {console} Example: comp Bryton S6 pc sheets
    only supports S6 and above"""
    new_list = await competitive_stats(player, console, season)
    file_name = pushto_excel_comp(new_list, season, player, tz)
    if file_type == "excel":
        await ctx.send(file=discord.File(file_name))
    elif file_type == "sheets":
        comp_link = excel_to_sheets(drive_service,file_name)
        await ctx.send(comp_link)
    else:
        ctx.send("file type is not supported")


@bot.command()
async def banner(ctx, player, week=None, season=current_season, console="steam", file_type="sheets", tz="US/Pacific"):
    """builds a excel file(compatible with google sheets) of stats, and progression for a specified season or week of iron banner for an individual destiny player
    Example: banner Brytron 8/27/19 S6 pc sheets or banner Brytron#11867 skip S6, pc, excel
    only supports S6 and above"""
    file_name = await banner_stats(player, console, season, week, tz)
    if file_type == "excel":
        await ctx.send(file=discord.File(file_name))
    elif file_type == "sheets":
        file_link = excel_to_sheets(drive_service, file_name)
        await ctx.send(file_link)
    else:
        ctx.send("file type is not supported")

@bot.command()
async def trials(ctx, player, week=None, season=current_season, console="steam", file_type="sheets", tz="US/Pacific"):
    """builds a excel file(compatible with google sheets) of stats, and progression for a specified season or week of trials for an individual destiny player
    Example: trials Brytron 8/27/19 S6 pc sheets or trials Brytron#11867 skip S6, pc, excel
    only supports S6 and above"""
    file_name = await trials_stats(player, console, season, week, tz)
    if file_type == "excel":
        await ctx.send(file=discord.File(file_name))
    elif file_type == "sheets":
        file_link = excel_to_sheets(drive_service, file_name)
        await ctx.send(file_link)
    else:
        ctx.send("file type is not supported")


@bot.command()
async def trialsteam(ctx, player1, player2, player3 = None, week=None, season=current_season, console="steam", file_type="sheets", tz="US/Pacific"):
    """builds a excel file(compatible with google sheets) of stats, and progression for a specified season or week of trials for an 2-3 guardians
    Example: *trialsteam Bryton#1234 "player2" "player3" skip S6, steam, excel, tz
    only supports S6 and above"""
    file_name = await build_trials_team(player1, player2, player3, console, season, week, tz)
    if file_type == "excel":
        await ctx.send(file=discord.File(file_name))
    elif file_type == "sheets":
        file_link = excel_to_sheets(drive_service, file_name)
        await ctx.send(file_link)
    else:
        ctx.send("file type is not supported")


@bot.command()
async def D2register(ctx,title,bungieid, console="steam"):
    """connects any user defined title to a bungieID"""
    output = await register(title, bungieid, console)
    if output == 1:
        await ctx.send("registration success")
    else:
        await ctx.send("registration failed")


@bot.command()
async def fight(ctx,player_1,player_2,console="steam"):
    """fight between two destiny players based on stats"""
    output = await fight_stats(player_1,player_2,console)
    await ctx.send(output)


@bot.command()
async def timeto(ctx, event, service=cal_service):
    """returns time to a future event from the community calendar"""
    out_event = find_event(service, event)
    time_dif = time_to(out_event.time).days
    await ctx.send(f"There is {time_dif} days til {out_event.summary}")


@bot.command()
async def timer(ctx, stop_time='10'):
    """sets up a countdown timer ex. *timer 10:00 for ten minutes"""
    time_all = stop_time.split(':')
    time_sec = 60*int(time_all[0]) + int(time_all[1])
    await ctx.send("timer is initialized")
    await asyncio.sleep(time_sec)
    await ctx.send("Timer is up")


@bot.command()
async def showcal(ctx):
    """posts the link to the public calendar"""
    await ctx.send(cal_link)


@bot.command()
async def addevent(ctx, event, month, day, start_time='12:00am', end_time="1:00am", service=cal_service):
    """adds and event to the calendar ex. *addevent event_name(no space allowed) Aug 16 4:00pm 5:00pm"""
    create_event(service, event, month, day, start_time, end_time)
    await ctx.send("event has been created")


@bot.command()
async def delevent(ctx, event_name, service=cal_service):
    """deletes a event specified by the event name ex. *delevent event_name"""
    delete_event(service,event_name)
    await ctx.send("event deleted")


def main():
    #initialize bot
    bot.run(TOKEN)


if __name__ == "__main__":
    main()

