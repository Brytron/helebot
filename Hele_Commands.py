import discord
import random
import os
from selectimage import *
from Destiny_connect import *
from pathlib import Path
import asyncio
from google_cal_connect import *
from google_spreedsheet_connect import *


from discord.ext import commands

TOKEN = 'Mzg4MTQyOTA1NjI3MjQ2NjEy.Xswoaw.0GCYsY8wohtKiAQ36HQ4QBP1TQQ'
#version 0.14
#
#warnings:
#playing sound files does not work natively on windows
#discord bot must be out of a voice channel to play another soundbite
#
# needs implementing:
# change requests to asnc function
# fix sound playback

description = '''Helebot version 0.2'''
bot = commands.Bot(command_prefix='*', description=description)
#initialize calendar
cal_service = initial_cal()
drive_service = initial_drive()
current_season = "S11"

pic_path = "wheresRyan_photos/"
Ryan = "Congohunter"
Bryton = "Bryton"
Tyler = "LtDangle"
cal_link = \
    "https://calendar.google.com/calendar?cid=ZGMybmZmbm43NjdiYmt1amdrbjAwOHVzb29AZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ"

path_baby = "soundbites/"

bs_playlist = (
"BS_AgainAgain.mp3", "BS_BeerCigChips.mp3", "BS_did you wash it.mp3", "BS_COmedown.mp3", "BS_dont get it.mp3",
"BS_dontlikethat.mp3", "BS_gonna kiss her.mp3", "BS_GOnna mary her.mp3", "BS_gottalove me.mp3", "BS_hotdonttouch.mp3",
"BS_howcomenobodyslaughing.mp3", "BS_ice cream.mp3", "BS_Im not happy.mp3", "BS_imascream.mp3", "BS_KICKIT.mp3",
"BS_kissthebabby.mp3", "BS_laugh.mp3", "BS_like you.mp3", "BS_loser.mp3", "BS_machinegun.mp3", "BS_nobed.mp3",
"BS_notthemama.mp3", "BS_oh.mp3", "BS_ohh a fight.mp3", "BS_ok.mp3", "BS_playagame.mp3", "BS_present.mp3",
"BS_puppets.mp3", "BS_readyornot.mp3", "Bs_she nice.mp3", "BS_shhlook.mp3", "BS_stayherewithyou.mp3",
"BS_thatsdiscusting.mp3",
"BS_The Monster gonna eat me.mp3", "BS_theyre yummy.mp3", "BS_want something good.mp3",
"BS_whatifthey dont have it.mp3",
"BS_yesmam.mp3", "BS_you dont look like us.mp3", "BS_youpromised.mp3", "BS_your chicken.mp3", "getaway getaway.mp3")


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
async def joke(ctx):
    """outputs a Joke"""
    await ctx.send("Ryan")


@bot.command()
@commands.has_permissions(administrator=True)
async def initial_cal(ctx):
    """initializes the calendar for the server"""
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
            time_to_event = time_to(tracked_event['start']['dateTime'])
            old_event_str = None
            event_time = parser.parse(tracked_event['start']['dateTime']).replace(tzinfo=None)
            while datetime.datetime.now() < next_check:
                if event_time > datetime.datetime.now():
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
                time_to_event = time_to(tracked_event['start']['dateTime'])
                old_event_str = event_str
            await asyncio.sleep(30)
        next_day = next_day + datetime.timedelta(days=1)
        last_event_list = event_list
        update_day = datetime.datetime.now().weekday()


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def flip(ctx):
    """flips a coin"""
    X = random.random()
    if X > 0.5:
        Y = 'Heads'
    else:
        Y = 'Tails'
    await ctx.send(Y)


@bot.command()
async def baby(ctx):
    """Plays a random soundbite from baby sinclair"""
    user = ctx.message.author
    print(user)
    try:
        voice_channel = user.voice.channel
        print(voice_channel)
        print("user is in ", voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return

    try:
        vc = await voice_channel.connect()
        print("connecting to voice channel")
        print(vc)
    except:
        print("voice channel already exists")

    bite = path_baby + random.choice(bs_playlist)
    try:
        vc.play(discord.FFmpegPCMAudio(bite), after=lambda e: print('done', e))
        print(bite," was played")
    except:
        print("playback error")
    await asyncio.sleep(9)
    await vc.disconnect()


@bot.command()
async def gdam(ctx):
    """plays a soundbite"""
    user = ctx.message.author
    print(user)
    try:
        voice_channel = user.voice.channel
        print(voice_channel)
        print("user is in ", voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return

    try:
        vc = await voice_channel.connect()
        print("connecting to voice channel")
        print(vc)
    except:
        print("voice channel already exists")

    bite = Path(path_baby + "ryan_Gdamn.mp3")
    try:
        vc.play(discord.FFmpegPCMAudio(bite), after=lambda e: print('done', e))
        print(bite," was played")
    except:
        print("playback error")
    await asyncio.sleep(5)
    await vc.disconnect()


@bot.command()
async def SHAM(ctx):
    """plays a soundbite"""
    user = ctx.message.author
    print(user)
    try:
        voice_channel = user.voice.channel
        print(voice_channel)
        print("user is in ", voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return

    try:
        vc = await voice_channel.connect()
        print("connecting to voice channel")
        print(vc)
    except:
        print("voice channel already exists")

    bite = Path(path_baby + "Sham.mp3")
    try:
        vc.play(discord.FFmpegPCMAudio(bite), after=lambda e: print('done', e))
        print(bite," was played")
    except:
        print("playback error")
    await asyncio.sleep(8.4)
    await vc.disconnect()


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

    await ctx.send(target.mention,file=discord.File(out))


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
@commands.has_permissions(administrator=True)
async def fuck(ctx, target: discord.Member):
    """Ryan says this"""
    user = ctx.message.author
    print(user)

    try:
        voice_channel = user.voice.channel
        print(voice_channel)
        print("user is in ", voice_channel)
    except:
        await ctx.send("User not in voice channel")
        return

    try:
        vc = await voice_channel.connect()
        print("connecting to voice channel")
        print(vc)
    except:
        print("voice channel already exists")
    await ctx.send(f"{target.mention} will be fucked off in 5 seconds")
    bite = Path(path_baby + "5secbyeby.mp3")

    try:
        vc.play(discord.FFmpegPCMAudio(bite), after=lambda e: print('done', e))
        print(bite," was played")
    except:
        print("playback error")

    await asyncio.sleep(6)
    await vc.disconnect()
    await asyncio.sleep(.25)
    await ctx.send(f"{target.mention} has been fucked off")
    await target.kick()


@fuck.error
async def fuck_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        ctx.send(f"{ctx.message.author.mention} does not have permission to fuck")


@bot.command()
async def pong(ctx,target: discord.Member):
    """mentions a discord member"""
    await ctx.send(target.mention)


@bot.command()
async def comp(ctx,player,season=current_season, console="steam", file_type="sheets", tz="US/Pacific"):
    """builds a excel file(compatible with google sheets) of stats, and progression for a specified season of competitive for an individual destiny player
    Query: comp {player} {season} {console} Example: comp Brytron S6 pc sheets
    only supports S6 and S7"""
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
    only supports S6 and S7"""
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
    only supports S6 and S7"""
    file_name = await trials_stats(player, console, season, week, tz)
    if file_type == "excel":
        await ctx.send(file=discord.File(file_name))
    elif file_type == "sheets":
        file_link = excel_to_sheets(drive_service, file_name)
        await ctx.send(file_link)
    else:
        ctx.send("file type is not supported")

@bot.command()
async def D2register(ctx,title,steamid):
    """connects any user definted title to a steamID"""
    output = await register(title, steamid)
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

