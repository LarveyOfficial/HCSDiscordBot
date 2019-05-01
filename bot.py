from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='$', case_insensitive=True)
prefix = "$"
version = "0.0.1"
TOKEN = 'NTY1MzUzMzU1Njc4MDU2NDQ4.XMmJcQ.wnBjUGE_AT9NjxJ-QWVbQbRcQTE'
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]
print('Complete Bot Operational')
@bot.command()
async def shutdown(ctx):
    if ctx.author.id in [245653078794174465]:
        await ctx.send(":wave:")
        await bot.change_presence(status='offline')
        await bot.logout()




bot.run(TOKEN)
