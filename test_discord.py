import discord
from discord.ext import commands

TOKEN = 'Mzg4MTQyOTA1NjI3MjQ2NjEy.XRrZPg.HN9i3nbzgdDASAPx1M1uOomCWgM'
description = "test"
bot = commands.Bot(command_prefix='*', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print()


bot.run(TOKEN)
