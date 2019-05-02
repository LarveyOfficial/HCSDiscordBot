from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='$', case_insensitive=True)
prefix = "$"
version = "0.0.2"
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]
print('HCS Bot Initiated')

if __name__== '__main__':
    import config


async def joinmsg(member):
    welcome = discord.utils.get(member.guild.channels, id=int(573171504234233888))
    embed = discord.Embed(title="Member Joined", description=member.name, color=0x1394ff)
    await welcome.send(embed=embed)


@bot.command()
async def shutdown(ctx):
    if ctx.author.id in [245653078794174465]:
        print(ctx.author.name + ' (' + str(ctx.author.id) + ')' + ' has requested a shutdown.')
        print('Shutting down')
        await ctx.send(":wave::wave:")
        await bot.change_presence(status='offline')
        await bot.logout()
    else:
        print(ctx.author.name + ' (' + str(ctx.author.id) + ')' + ' has requested a shutdown.')
        print('But they do not have enough permissions')

@bot.event
async def on_member_join(member):
    await joinmsg(member)





bot.run(config.TOKEN)
