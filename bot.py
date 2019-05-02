from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='$', case_insensitive=True)
prefix = "$"
version = "0.0.5"
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


async def playerjoin(member):
    print('New player joined... Making Setup Room')
    name = str(member.id)
    overwrites = {
        member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True)
    }
    category = discord.utils.get(member.guild.categories, name="Setup", overwrites=overwrites)
    if not category:
        await member.guild.create_category_channel(name='Setup')
        category = discord.utils.get(member.guild.categories, name="Setup")

    channel = await member.guild.create_text_channel(name, overwrites=overwrites, category=category)
    print("Creating new setup for " + member + ".")
    await channel.send("Welcome " + member + " to the HCS Discord Server!")

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

@bot.event
async def on_member_join(member):
    await playerjoin(member)


bot.run(config.TOKEN)
