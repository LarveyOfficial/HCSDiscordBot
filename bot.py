from discord.ext import commands
import discord, datetime

bot = commands.Bot(command_prefix='$', case_insensitive=True)
prefix = "$"
version = "0.0.1"
TOKEN = ''
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]

@bot.command()
async def stop(ctx):
    if ctx.author.id in [245653078794174465]:
        await ctx.send(":wave:")
        await bot.change_presence(status='offline')
        await bot.logout()


bot.run(TOKEN)
