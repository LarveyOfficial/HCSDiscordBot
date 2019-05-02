from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='$', case_insensitive=True)
prefix = "$"
version = "0.0.2"
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]

if __name__== '__main__':
    import config

@bot.event
async def on_ready():
    guilds = list(bot.guilds)
    print("Connected to " + str(len(bot.guilds)) + " server(s):")
    for x in range(len(guilds)):
        print('  ' + guilds[x-1].name)

async def joinmsg(member):
    welcome = discord.utils.get(member.guild.channels, id=int(573171504234233888))
    embed = discord.Embed(title="Member Joined", description=member.name, color=0x1394ff)
    await welcome.send(embed=embed)


async def playerjoin(ctx):
    print('New player joined... Making Setup Room')
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True)
    }
    category = discord.utils.get(ctx.guild.categories, name="Setup")
    if not category:
        await ctx.guild.create_category_channel(name='Setup')
        category = discord.utils.get(ctx.guild.categories, name="Setup")

    channel = await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)
    print("Creating New Setup")
    await channel.send("Hello World")

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
    await playerjoin()


bot.run(config.TOKEN)
