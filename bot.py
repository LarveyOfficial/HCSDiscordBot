from discord.ext import commands
import discord, time, asyncio, pymongo, string, random
if __name__ == '__main__':
    import config


bot = commands.Bot(command_prefix='$', case_insensitive=True)
version = "Alpha 0.1.0"
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]

# lol don't touch this
mongo_db = pymongo.MongoClient("mongodb://hytexxity:hytexxity@cluster0-shard-00-00-7rhwq.mongodb.net:27017,cluster0-shard-00-01-7rhwq.mongodb.net:27017,cluster0-shard-00-02-7rhwq.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
hcs_db = mongo_db['HCS']
user_col = hcs_db['users']


def make_doc(user_name=None, user_id=None, code=None, grade=None, roles=None, student_id=None, verified=False):
    doc_ = {'user_name': user_name, 'user_id': str(user_id), 'code': code, 'grade': str(grade), 'roles': roles, 'student_id': str(student_id), 'verified': verified}  # 'code' == None if verified and verified will be true
    return doc_


def gen_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def check_for_doc(check_key, check_val, check_key2=None, check_val2=None):
    if not check_key2 or not check_val2:
        the_doc = user_col.find_one({check_key: check_val})
        if the_doc:
            return True
        else:
            return False
    else:
        the_doc = user_col.find_one({check_key: check_val, check_key2: check_val2})
        if the_doc:
            return True
        else:
            return False


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
    the_doc = user_col.find_one({'user_id': str(member.id), 'verified': True})
    if the_doc:
        print("user is already registered")
        return
    else:
        await giverole(member)

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
            if reaction.emoji == "🇲":
                print(member.name + " choose middleschool, saving to file...")
                await channel.send('-Saving (Middle School)')




                their_code=gen_code()
                if check_for_doc("user_id", str(member.id)):
                    user_col.insert_one(make_doc(member.name, member.id, their_code, 'middle', None, None, False))

                    # send code to email?

                break

            elif reaction.emoji == "🇭":
                print(member.name + " choose highschool, saving to file...")
                await channel.send('-Saving (High School)')

                msg2 = await channel.send("Whats your grade?\n\nA: Freshmen\nB: Sophmore\nC: Junior\nD: Senior")
                await msg2.add_reaction("🇦")
                await msg2.add_reaction("🇧")
                await msg2.add_reaction("🇨")
                await msg2.add_reaction("🇩")
                while True:
                    reaction2, react_member2 = await bot.wait_for('reaction_add')
                    if react_member2.id is member.id:
                        if reaction2.emoji == "🇦":
                            print(member.name + " Choose Freshmen... ew")
                            await channel.send('-Saving (9th Grade)')
                            gradeselect = "9th"
                            break
                        elif reaction2.emoji == "🇧":
                            print(member.name + " Choose Sophmore")
                            await channel.send('-Saving (10th Grade)')
                            gradeselect = "10th"
                            break
                        elif reaction2.emoji == "🇨":
                            print(member.name + " Choose Junior")
                            await channel.send('-Saving (11th Grade)')
                            gradeselect = "11th"
                            break
                        elif reaction2.emoji == "🇩":
                            print(member.name + " Choose Senior")
                            await channel.send('-Saving (12th Grade)')
                            gradeselect = "12th"
                            break
                        else:
                            print("not right emoji")
                            continue
                    else:
                        print("not right user")
                        continue


                their_code=gen_code()
                print("generated code: "+ str(their_code))
                if check_for_doc("user_id", str(member.id)):
                    print("saving...")
                    user_col.insert_one(make_doc(member.name, member.id, their_code, gradeselect, None, None, False))
                    print("saved.")

                    #send code to email?


                break

            else:
                continue


@bot.event
async def on_member_remove(member):
    if check_for_doc("user_id", str(member.id)):
        user_col.delete_many({'user_id': str(member.id), 'verified': False})

    channel = discord.utils.get(member.guild.text_channels, name=str(member.id))
    if channel:

        print(str(member.id) +" left, deleting their setup")
        await channel.delete()


@bot.command()
async def shutdown(ctx):
    if ctx.author.id in owner_ids:
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
    await playerjoin(member)
    await joinmsg(member)
bot.run(config.TOKEN)
