from discord.ext import commands
import discord, time, asyncio, pymongo, doc_maker
if __name__ == '__main__':
    import config


bot = commands.Bot(command_prefix='$', case_insensitive=True)
version = "Alpha 0.1.0"
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]


def make_doc(user_name, user_id, code=None, grade=None, ):
    doc_ = {'user_name': user_name, 'user_id': str(user_id), 'code': code, 'grade': grade, ''}  # 'code' == None if verified
    return doc_

# lol don't touch this
mongo_db = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (config.username, config.password, config.host, config.port))
hcs_db = mongo_db['db']
user_col = hcs_db['users']



@bot.event
async def on_ready():
    guilds = list(bot.guilds)
    print("HCS Discord Bot "+version)
    print("Connected to " + str(len(bot.guilds)) + " server(s):")
    for x in range(len(guilds)):
        print('  ' + guilds[x-1].name)

async def joinmsg(member):
    welcome = discord.utils.get(member.guild.channels, id=int(573171504234233888))
    embed = discord.Embed(title="Member Joined", description=member.name, color=0x1394ff)
    await welcome.send(embed=embed)


async def playerjoin(member):
    print('New player joined... Making Setup Room')
    overwrites = {
        member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True)
    }

    category = discord.utils.get(member.guild.categories, name="Setup")
    if not category:
        await member.guild.create_category_channel(name='Setup')
        category = discord.utils.get(member.guild.categories, name="Setup")

    channel = await member.guild.create_text_channel(str(member.id), overwrites=overwrites, category=category)
    print("Creating new setup for " + str(member) + ".")
    
    msg = await channel.send("Welcome " + str(member) + " to the HCS Discord Server!\nLets Start the Setup!\nAre you from the Highschool, or the Middleschool? React Acordingly")
    await msg.add_reaction("🇭")
    await msg.add_reaction("🇲")

    while True:
        reaction, react_member = await bot.wait_for('reaction_add')
        if react_member.id is member.id:
            if reaction.emoji == "🇲" or reaction.emoji== "🇭":
                if reaction.emoji == "🇲":
                    print(member.name + " choose middleschool, saving to file...")
                    await channel.send('-Saving (Middle School)')
                    user_col.insert_one(make_doc())
                    break
                elif reaction.emoji == "🇭":
                    print(member.name + " choose highschool, saving to file...")
                    await channel.send('-Saving (High School)')
                    break
                else:
                    continue


@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name=str(member.id))
    if channel:
        
        print(str(member.id) +" left, deleting their setup")
        await channel.delete()

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

async def giverole(member):
    roleid = 573953106417680409
    role = discord.utils.get(member.guild.roles, id=roleid)
    await member.add_roles(role)
    print(member.name + "(" + str(member.id) + ") " + "has Joined the discord adding them to the role: " + str(role))

@bot.event
async def on_member_join(member):
    if member.id==bot.user.id:
        return
    await giverole(member)
    await playerjoin(member)

bot.run(config.TOKEN)
