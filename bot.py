from discord.ext import commands
import pymongo, praw, re, time, os, datetime, asyncio, discord, time, random, requests

version = "0.0.1"
bot = commands.bot(command_prefix='$', case_insensitive='true')
prefix = '$'
TOKEN = ''
print("Hello World")

@bot.event
async def on_guild_join(guild):
    make_file(guild)

@bot.command()
async def test(ctx):
    await ctx.send("Ok")
