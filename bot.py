from __future__ import print_function
from discord.ext import commands
import discord, time, asyncio, pymongo, string, random, csv, smtplib
from generator import KajGenerator
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
if __name__ == '__main__':
    import config


bot = commands.Bot(command_prefix='$', case_insensitive=True)
version = "Alpha 0.1.5"
bot.remove_command('help')
print("Loading....")
owner_ids=[245653078794174465]
gen = KajGenerator()
role_list = ['band', 'ssb', 'minecraft', 'bedwars', 'communist', 'art', 'languages', 'gamer']

# lol don't touch this
client = pymongo.MongoClient(config.uri)
print("authenticated with mongo database")
hcs_db = client.HCS
user_col = hcs_db.users
print('collected documents (' + str(user_col.count_documents({})) + ")")


async def sendemail(studentemail, emailcode):
    body = "Your HCSDiscord Verification Code is \n\n" + str(emailcode)+"\n\nPlease use $verify "+str(emailcode)+ " in your setup channel\nYour code will Expire in 24hours\n\n" + "If you don't believe this was you please msg Larvey#0001 on Discord."
    emailsubject = "HCSDiscord Authenitcation"

    emailmsg = MIMEMultipart()
    emailmsg['To'] = studentemail
    emailmsg['From'] = config.mailfromAddress
    emailmsg['Subject'] = emailsubject
    emailmsg.attach(MIMEText(body, 'plain'))
    message = emailmsg.as_string()

    emailserver = smtplib.SMTP(config.mailfromserver)
    emailserver.starttls()
    emailserver.login(config.mailfromAddress, config.mailfrompassword)
    await log("Sending Email....")
    emailserver.sendmail(config.mailfromAddress, studentemail, message)
    await log("Email Sent to " + studentemail)
    emailserver.quit()


async def log(message):
    if message is not None:
        log_guild = bot.get_guild(config.log_guild)
        log_channel = discord.utils.get(log_guild.channels, id=config.log_channel)
        print(message)
        await log_channel.send('['+str(datetime.datetime.utcnow())+'# INFO:] '+message)


async def log_error(message):
    if message is not None:
        log_guild = bot.get_guild(config.log_guild)
        log_channel = discord.utils.get(log_guild.channels, id=config.log_channel)
        print('# ERROR:'+message)
        await log_channel.send('['+str(datetime.datetime.utcnow())+'# ERROR:] '+message)


def MakeEmbed(author=None, author_url=None, title=None, description=None, url=None, thumbnail=None, doFooter=False, color=None):
    if url is not None:
        if color is None:
            embed = discord.Embed(title=title, description=description, url=url, color=discord.Color.dark_blue())
        else:
            embed = discord.Embed(title=title, description=description, url=url, color=color)
    else:
        if color is None:
            embed = discord.Embed(title=title, description=description, color=discord.Color.dark_blue())
        else:
            embed = discord.Embed(title=title, description=description, color=color)

    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if author is not None and author_url is not None:
        embed.set_author(name=author, url=author_url)
    if doFooter is True:
        embed.set_footer(text="HCS discord bot.", icon_url=bot.user.avatar_url)
    return embed


def make_doc(user_name=None, user_id=None, code=None, grade=None, student_id=None, verified=False):
    doc_ = {'user_name': user_name, 'user_id': str(user_id), 'code': code, 'grade': str(grade), 'student_id': str(student_id), 'verified': verified}  # 'code' == None if verified and verified will be true
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


@bot.command()
async def ticket(ctx, *, name:str = None):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True),
    }
    ticketcategory = discord.utils.get(ctx.guild.categories, name="tickets")
    if not ticketcategory:
        await ctx.guild.create_category_channel(name="tickets")
        ticketcategory = discord.utils.get(ctx.guild.categories, name="tickets")
    ticketname = "ticket-{0}".format(ctx.author.id)
    ticketchannelmade = discord.utils.get(ctx.guild.channels, name=ticketname)
    if not ticketchannelmade:
        embed = MakeEmbed(title="Ticket", description="Making your Ticket...", doFooter=True)
        await ctx.send(embed=embed)
        ticketchannel = await ctx.guild.create_text_channel(ticketname, overwrites=overwrites, category=ticketcategory)
        await log(ctx.author.name + "Needs A Ticket..")
        ticketembed = MakeEmbed(title="Ticket",description="Welcome " + ctx.author.mention + " This is your Ticket! <@&543060916086767617>", doFooter=True)
        await ticketchannel.send(embed=ticketembed)
    else:
        ticketExists = MakeEmbed(title="ERROR",description="You already have a ticket open!", doFooter=True, color = discord.Color.dark_red())
        await ctx.send(embed=ticketExists)


@bot.command()
async def adduser(ctx, member:discord.Member = None):
    if member is not None:
        category = discord.utils.get(ctx.guild.categories, name="tickets")
        if category is None:
            error_embed = MakeEmbed(title="ERROR", description="an error has occured. There is no Ticket category.")
            await ctx.send(embed=error_embed)
            return
        if ctx.channel.category_id == category.id:
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
            successadd = MakeEmbed(title="Ticket", description="I have added " + member.mention + " to this Ticket!")
            await ctx.send(embed=successadd)
        else:
            notinticket = MakeEmbed(title="ERROR", description="This command must be made in a Ticket Channel!", doFooter=True, color=discord.Color.dark_red())
            await ctx.send(embed=notinticket)
    else:
        membernotexist = MakeEmbed(title="ERROR", description="Please Specify a User!", doFooter=True, color=discord.Color.dark_red())
        await ctx.send(embed=membernotexist)
        return


@bot.command()
async def rmuser(ctx, member:discord.Member = None):
    if member is not None:
        category = discord.utils.get(ctx.guild.categories, name="tickets")
        if category is None:
            error_embed = MakeEmbed(title="ERROR", description="an error has occured. There is no Ticket category.")
            await ctx.send(embed=error_embed)
            return
        if ctx.channel.category_id == category.id:
            await ctx.channel.set_permissions(member, read_messages=False, send_messages=False)
            successrm = MakeEmbed(title="Ticket", description="I have removed " + member.name + " from this Ticket.")
            await ctx.send(embed=successrm)
        else:
            notinticket = MakeEmbed(title="ERROR", description="This command must be made in a Ticket Channel!", doFooter=True, color=discord.Color.dark_red())
            await ctx.send(embed=notinticket)
            return
    else:
        membernotexist = MakeEmbed(title="ERROR", description="Please Specify a User!", doFooter=True, color=discord.Color.dark_red())
        await ctx.send(embed=membernotexist)
        return


@bot.command()
async def close(ctx):
    ticketcategory = discord.utils.get(ctx.guild.categories, name="tickets")
    roleid = 543060916086767617
    if ctx.channel.category_id == ticketcategory.id:
        if ctx.channel.name == "ticket-{0}".format(ctx.author.id):
            await ctx.channel.delete()
        elif roleid in [y.id for y in ctx.author.roles]:
            await ctx.channel.delete()
        else:
            noturticketlol = MakeEmbed(title="ERROR", description="This is not your Ticket!", doFooter=True, color=discord.Color.dark_red())
            await ctx.send(embed=noturticketlol)

    else:
        notinticketcategory = MakeEmbed(title="ERROR", description="This command can only be done in a ticket!", doFooter=True, color=discord.Color.dark_red())
        await ctx.send(embed=notinticketcategory)


@bot.group()
async def help(ctx):
    if ctx.invoked_subcommand is None:
        embed = MakeEmbed(title="Help", description="The following commands can be used by anyone:\n-role\n-rmrole\n-ping\n-ticket\n-identify\n-help <command>",doFooter=True)
        await ctx.send(embed=embed)


@help.command()
async def role(ctx):
    embed = MakeEmbed(title="Help - Role", description="$role <role> to add yourself to a role.", doFooter=True)
    await ctx.send(embed=embed)


@help.command()
async def rmrole(ctx):
    embed = MakeEmbed(title="Help - RmRole", description="$rmrole <role> to remove yourself from a role.", doFooter=True)
    await ctx.send(embed=embed)


@help.command()
async def ping(ctx):
    embed = MakeEmbed(title="Help - Ping", description="$ping to check bots ping.", doFooter=True)
    await ctx.send(embed=embed)

@help.command()
async def identify(ctx):
    embed = MakeEmbed(title="Help - Identify", description="$identify <member> to see a user's real name.", doFooter=True)
    await ctx.send(embed=embed)


@help.command()
async def ticket(ctx):
    embed = MakeEmbed(title="Help - Ticket", description="$ticket - To make a new ticket\n$close - To close a ticket\n$adduser <user> - To add a user to a Ticket\n$rmuser <user> - To remove user from a Ticket", doFooter=True)
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    embed=MakeEmbed(title='🏓 PONG 🏓', description="**{0} ms**".format(round(bot.latency * 1000, 1)))
    await ctx.send(embed=embed)


@bot.command()
async def purge_all(ctx):
    msg = await ctx.send('checking user...')
    if ctx.author.id in owner_ids:
        await log('owner requested purge of database')
        await log('purging...')
        await msg.edit(content='purging...')
        user_col.delete_many({})
        await msg.edit(content='database purged!')
        print('database purged')
        return
    else:
        print('user requested purge of database: '+ctx.author.name+'\nbut was denied.')
        await msg.edit(content="you can't do that lmao")
        return


@bot.event
async def on_ready():
    await log("bot logged in with version: "+version)
    await log("Connected to " + str(len(bot.guilds)) + " server(s):")
    await log("Bot Connected to Gmail Servers")
    print('Started Status Loop')
    while True:
        a_name = gen.MakeUsername(1)
        a_name[0] = a_name[0].replace('_', ' ')
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=a_name[0]))
        print('changed name to '+ a_name[0])
        await asyncio.sleep(60)


async def make_new_channel(member):
    overwrites = {
        member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, add_reactions=False),
        bot.user: discord.PermissionOverwrite(read_messages=True)
    }

    category = discord.utils.get(member.guild.categories, name="Setup")
    if not category:
        await member.guild.create_category_channel(name='Setup')
        category = discord.utils.get(member.guild.categories, name="Setup")

    channel = await member.guild.create_text_channel(str(member.id), overwrites=overwrites, category=category)
    await log("Creating new setup for " + str(member) + ".")
    return channel


async def select_middle_school(member, channel):
    await log(member.name + " choose middleschool")
    await channel.send('-Saving (Middle School)')
    roleid = 546025605221711882
    role_ = discord.utils.get(member.guild.roles, id=roleid)
    await member.add_roles(role_)
    their_code = gen_code()
    if not check_for_doc("user_id", str(member.id)):
        user_col.insert_one(make_doc(member.name, member.id, their_code, 'Middle School', None, False))
        await get_student_id(member, channel)

        # send code to email?


async def get_student_id(member, channel):
    await channel.send("*Step three:* Please type your student ID.")
    while True:
        idmsg = await bot.wait_for('message')
        if idmsg.author.id is member.id:
            student_id6 = ''.join(filter(lambda x: x.isdigit(), idmsg.content))
            try_for_id = user_col.find_one({'student_id': str(student_id6)})
            if try_for_id is not None:
                await channel.send('ERROR: That ID is already In use. Please use another one. Contact Larvey#0001 if this *is* your student ID.')
                continue
            if student_id6 is '':
                await channel.send('ERROR: Thats not a Valid ID')
                continue
            if await compare_id(idmsg.channel, idmsg.author, student_id6):
                return
            else:
                continue
        else:
            continue


@bot.command()
async def verify(ctx, code: str=None):
    if code is not None:
        doc = user_col.find_one({'code': code, 'user_id': str(ctx.author.id)})
        if doc is not None:
            updated_tag = {"$set": {'verified': True, 'code': None}}
            user_col.update_one({'code': code, 'user_id': str(ctx.author.id)}, updated_tag)
            await ctx.author.send("Yeah Boi U got **Verified**!")
            roleid = 576127240669233152
            role_ = discord.utils.get(ctx.guild.roles, id=roleid)
            await ctx.author.remove_roles(role_)
            channel = discord.utils.get(ctx.guild.text_channels, name=str(ctx.author.id))
            await joinmsg(ctx.author)
            if channel:
                await log(str(ctx.author.id) + " is verified, deleting their setup")
                await channel.delete()


async def compare_id(channel, member, student_id):
    await log('started comparing ids for {}'.format(member.name))
    confirmmsg = await channel.send('Searching for your Student ID...')
    with open('eggs.csv', newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            student_id9 = ''.join(filter(lambda x: x.isdigit(), row[30]))
            if str(student_id) in row[30] and len(str(student_id)) == 8:
                await log("student ID matched: "+row[30] + ' - ' + student_id9)
                their_doc = user_col.find_one({'user_id': str(member.id)})
                if their_doc is not None:
                    #print('verify using this... $verify '+ their_doc['code'])
                    emailcode = their_doc['code']
                    studentemail = str(student_id)+"@hartlandschools.us"
                    #await last_message.delete()
                    await confirmmsg.edit(content="Found that Student ID! ("+student_id+") "+"Would you like us to send you an email to confirm it is you?")
                    react_yes = await confirmmsg.add_reaction("🇾")
                    react_no = await confirmmsg.add_reaction("🇳")
                    while True:
                        reaction3, react_member3 = await bot.wait_for('reaction_add')
                        if react_member3.id is member.id:
                            if reaction3.emoji == "🇾":
                                await log(member.name + " has confirmed that "+student_id+" is their student ID. Sending Email.")
                                await log("Email Address is: "+studentemail)
                                await channel.send("We have sent you an email with a Verifiation Code to "+studentemail+" Please use $verify <VERIFICATION CODE>")
                                await sendemail(studentemail, emailcode)
                                updated_tag = {"$set": {'student_id': str(student_id)}}
                                user_col.update_one({'user_id': str(member.id)}, updated_tag)
                                await log('updated user id to be the user id they have so yeah. Now ima send an email. *dabs*')
                                return True
                            if reaction3.emoji == "🇳":
                                await confirmmsg.edit(content="Not sending email. (In order to complete the setup, you will need to verify by email.)\nPlease type your student ID.")
                                await confirmmsg.remove_reaction("🇾", bot.user)
                                await confirmmsg.remove_reaction("🇳", bot.user)
                                await confirmmsg.remove_reaction("🇳", react_member3)
                                return False

        await log_error('No ID Found (Welp.. Thats a Wrap)')
        await confirmmsg.edit(content='Sorry, That ID was not Found. Please Try Again')
        return False


async def select_high_school(member, channel):
    print(member.name + " choose highschool")

    msg2 = await channel.send("*Step two:* Whats your grade?\n\n🇦: Freshmen,\n🇧: Sophmore,\n🇨: Junior,\n🇩: Senior\n\nReact accordingly.")
    await msg2.add_reaction("🇦")
    await msg2.add_reaction("🇧")
    await msg2.add_reaction("🇨")
    await msg2.add_reaction("🇩")
    while True:
        reaction2, react_member2 = await bot.wait_for('reaction_add')
        if react_member2.id is member.id:
            if reaction2.emoji == "🇦":
                await log(member.name + " Choose Freshmen... ew")
                await msg2.edit(content='9th grade selected')
                gradeselect = "Freshmen"
                roleid = 543060124600762406
                role_ = discord.utils.get(member.guild.roles, id=roleid)
                await member.add_roles(role_)
                break
            elif reaction2.emoji == "🇧":
                await log(member.name + " Choose Sophmore")
                await msg2.edit(content='10th grade selected')
                gradeselect = "Sophomore"
                roleid = 543060215646388224
                role_ = discord.utils.get(member.guild.roles, id=roleid)
                await member.add_roles(role_)
                break
            elif reaction2.emoji == "🇨":
                await log(member.name + " Choose Junior")
                await msg2.edit(content='11th grade selected')
                gradeselect = "Junior"
                roleid = 543060357191827478
                role_ = discord.utils.get(member.guild.roles, id=roleid)
                await member.add_roles(role_)
                break
            elif reaction2.emoji == "🇩":
                await log(member.name + " Choose Senior")
                await msg2.edit(content='12th grade selected')
                gradeselect = "Senior"
                roleid = 543060511441289216
                role_ = discord.utils.get(member.guild.roles, id=roleid)
                await member.add_roles(role_)
                print(member.name + " Choose Senior")
                break
            else:
                continue
        else:
            continue

    await log("generating code...")
    their_code = gen_code()
    await log("generated code: " + str(their_code))
    if not check_for_doc("user_id", str(member.id)):
        await log("saving...")
        user_col.insert_one(make_doc(member.name, member.id, their_code, gradeselect, None, False))
        await log("saved.")
        await get_student_id(member, channel)

        # send code to email?


async def joinmsg(member):
    welcome = discord.utils.get(member.guild.channels, id=int(543062297749487627))
    embed = discord.Embed(title="Member Joined", description=member.name, color=discord.Color.dark_blue())
    await welcome.send(embed=embed)


async def playerjoin(member):
    checkdoc = user_col.find_one({'user_id': str(member.id), 'verified': True})
    if checkdoc is not None:
        grade_role = discord.utils.get(member.guild.roles, name=checkdoc['grade'])
        if grade_role is not None:
            await member.add_roles(grade_role)
        await log("user {} joined. but is already registered".format(member.name))
        return
    else:
        await giverole(member)

    await log('New player joined... Making Setup Room')
    channel = await make_new_channel(member)

    msg = await channel.send("**Welcome " + str(member) + " to the HCS Discord Server!**\n\n__Lets Start the Setup!__ \n*Step one:* Are you from the High School, or the Middle School? React Accordingly.")
    await msg.add_reaction("🇭")
    await msg.add_reaction("🇲")

    while True:
        reaction, react_member = await bot.wait_for('reaction_add')
        if react_member.id is member.id:
            if reaction.emoji == "🇲":
                await select_middle_school(member, channel)
                break

            elif reaction.emoji == "🇭":
                await select_high_school(member, channel)
                break

            else:
                continue


@bot.command()
async def role(ctx, _role: str=None):
    if _role is None:
        embed = MakeEmbed(title="List of Roles:", description=(', '.join(role_list)),doFooter=True)
        await ctx.send(embed=embed)
    else:
        if _role.lower() in role_list:
            get_role = discord.utils.get(ctx.guild.roles, name=_role.lower())
            if get_role is not None:
                await ctx.author.add_roles(get_role)
                await log("Adding " + str(ctx.author) + " To Role: " + str(get_role))
                embedconfirm = MakeEmbed(title="Added you to Role:", description=str(get_role), doFooter=True)
                await ctx.send(embed=embedconfirm)
            else:
                await ctx.send("That Role Dosen't Exist")
        else:
            await ctx.send("That Role Dosen't Exist")


@bot.command()
async def rmrole(ctx, _role: str=None):
    if _role is None:
        embed = MakeEmbed(title="List of Roles:", description=(', '.join(role_list)),doFooter=True)
        await ctx.send(embed=embed)
    else:
        get_role = discord.utils.get(ctx.guild.roles, name=_role.lower())
        if get_role is not None and get_role in ctx.author.roles:
            await ctx.author.remove_roles(get_role)
            await log("Removing " + str(ctx.author) + " From Role: " + str(get_role))
            embedconfirm = MakeEmbed(title="Removed you From Role:", description=str(get_role), doFooter=True)
            await ctx.send(embed=embedconfirm)
        else:
            embederror = MakeEmbed(title="ERROR", description="You don't have that Role!", doFooter=True, color=discord.Color.dark_red())
            await ctx.send(embed=embederror)


@bot.event
async def on_member_remove(member):
    if check_for_doc("user_id", str(member.id)):
        user_col.delete_many({'user_id': str(member.id), 'verified': False})

    channel = discord.utils.get(member.guild.text_channels, name=str(member.id))
    if channel:

        await log(str(member.id) + " left, deleting their setup")
        await channel.delete()


@bot.command()
async def shutdown(ctx):
    if ctx.author.id in owner_ids:
        await log(ctx.author.name + ' (' + str(ctx.author.id) + ')' + ' has requested a shutdown.')
        await log('Shutting down')
        await ctx.send(":wave::wave:")
        await bot.change_presence(status='offline')
        await bot.logout()
    else:
        await log_error(ctx.author.name + ' (' + str(ctx.author.id) + ')' + ' has requested a shutdown. But they do not have enough permissions')


async def giverole(member):
    roleid = 576127240669233152
    role_ = discord.utils.get(member.guild.roles, id=roleid)
    await member.add_roles(role_)
    await log(member.name + "(" + str(member.id) + ") " + "has Joined the discord adding them to the role: " + str(role))


@bot.event
async def on_command_error(ctx, error):
    await log_error(str(error))
    raise error


@bot.command(name='identify')
async def identify(ctx, name: discord.Member=None):
    if name is None:
        embed=MakeEmbed(title="Identify", description="Use $identify to identify somones name.")
        await ctx.send(embed=embed)
    else:
        if name.id:
            userid = user_col.find_one({'user_id': str(name.id)})
            if userid is None:
                nouser = MakeEmbed(title="ERROR", description="User does not Exist.")
                await ctx.send(embed=nouser)
            else:
                studentid = str(userid['student_id'])
                with open('eggs.csv', newline='') as csvfile:
                    csvReader = csv.reader(csvfile, delimiter=',')
                    for row in csvReader:
                        student_id12 = ''.join(filter(lambda x: x.isdigit(), row[30]))
                        if str(student_id12) in row[30] and str(student_id12) == str(studentid):
                            firstname = row[1]
                            lastname = row[3]
                            discordname = str(userid['user_name'])
                            await log("Finding "+discordname+"'s name..")
                            studentname=MakeEmbed(title="Identify", description=discordname+"'s "+" name is: " + firstname + " " + lastname)
                            await log("Name found, sending")
                            await ctx.send(embed=studentname)
        else:
            nouser=MakeEmbed(title="ERROR", description="User does not Exist.", color=discord.Color.dark_red(), doFooter=True)
            ctx.send(embed=nouser)

async def purge_unverified():
    print("Initiated Inactive Loop")
    while not bot.is_closed():
        await asyncio.sleep(60*60*24)
        accounts_deleted = 0
        to_delete = user_col.find({'verified':False, 'student_id':None})
        for doc in to_delete:
            a_member = discord.utils.get(bot.get_all_members(), id=int(doc['user_id']))
            if a_member is not None and a_member.guild.id is config.guild_id:
                a_member.send('you have been kicked from the server for inactivity during setup. please re-join if you want to complete the setup: \n\n'+config.invite_url)
                a_member.kick()
                accounts_deleted = accounts_deleted+1
                user_col.delete_many({'user_id': str(a_member.id)})

        await log("deleted {} unverified users".format(str(accounts_deleted)))


@bot.event
async def on_member_join(member):
    if member.id==bot.user.id:
        return
    await playerjoin(member)


bot.loop.create_task(purge_unverified())
bot.run(config.TOKEN)
