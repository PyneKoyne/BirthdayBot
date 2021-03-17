import discord
import calendar
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import pytz

Token = 'Redacted'
# Opens the channel ID
channel = open('Channel.txt', 'r')
# birthdays is the file
birthdays = open('Birthdays.txt', 'r')
# birthday_list is birthdays but in list form
birthday_list = birthdays.read().split("\n")
# current birthday is for when a regular member adds a birthday
# The first 2 are the name and birthday, the third is the message, the fourth is the number of votes
current_birthday = ['', '', '', 0]
# If there is a birthday list on, tells the bot which page it is on
page = [0, 0, 0, False]

# The discord Client
intents = discord.Intents.default()
intents.reactions = True
client = commands.Bot(command_prefix='b!', intents=intents)
client.remove_command('help')


def delete_n(del_n):
    global birthday_list
    global birthdays

    birthdays = open('Birthdays.txt', 'w')
    deleted = ''
    counter = 0

    # For loops through the file copying each line except the one deleted
    for i in range(len(birthday_list)):
        # Checks if the increment is not at the deleted birthday and if it is the last element

        if i != del_n - 1 and counter == 0:
            birthdays.write(birthday_list[i])
            counter += 1

        # Checks if it's the last element
        elif i != del_n - 1:
            birthdays.write('\n' + birthday_list[i])
            counter += 1

        # If it is the deleted birthday
        else:
            deleted = birthday_list[i]

    return deleted


def partition(arr, low, high):
    i = (low - 1)  # index of smaller element
    pivot = arr[high]  # pivot

    for j in range(low, high):

        # If current element is smaller than or
        # equal to pivot
        if arr[j] <= pivot:
            # increment index of smaller element
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quick_sort(arr, low, high):
    if len(arr) == 1:
        return arr
    if low < high:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high)

        # Separately sort elements before
        # partition and after partition
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)


# The number of days in months suck
def day(months, days):
    eastern = pytz.timezone('Canada/Atlantic')
    today = datetime.now(eastern)

    print(today.strftime('%d'))

    if int(today.strftime('%m')) < months:
        months -= int(today.strftime('%m'))
        days = days - int(today.strftime('%d'))

    elif int(today.strftime('%m')) > months:
        months += 12 - int(today.strftime('%m'))
        days = days - int(today.strftime('%d'))
    else:
        if int(today.strftime('%d')) == days:
            return 0
        elif int(today.strftime('%d')) > days:
            return 364 + days - int(today.strftime('%d'))
        else:
            return days - int(today.strftime('%d'))

    total_days = months * 31

    print(months)
    # February
    if months > 1:
        total_days -= 3

    # April
    if months > 3:
        total_days -= 1

    # June
    if months > 5:
        total_days -= 1

    # September
    if months > 8:
        total_days -= 1

    # November
    if months > 10:
        total_days -= 1

    total_days += days
    return total_days


# Sorts the birthdays
def sort_birthday():
    global birthdays
    global birthday_list

    birthday_days = []
    for i in range(len(birthday_list)):
        date = birthday_list[i].split('|')[1].split('/')

        birthday_days.append(day(int(date[1]), int(date[0])))

    quick_sort(birthday_days, 0, len(birthday_days) - 1)

    birthdays = open('Birthdays.txt', 'w')
    print('check1')
    for i in range(len(birthday_days)):
        for j in range(len(birthday_list)):

            date = birthday_list[j].split('|')[1].split('/')

            if birthday_days[i] == day(int(date[1]), int(date[0])) and i == 0:
                birthdays.write(birthday_list[j])
                del birthday_list[j]
                break

            elif birthday_days[i] == day(int(date[1]), int(date[0])) and i != 0:
                birthdays.write('\n' + birthday_list[j])
                del birthday_list[j]
                break

    print('check3')
    birthdays = open('Birthdays.txt', 'r')
    birthday_list = birthdays.read().split("\n")


def birthday_list_embed():
    global birthdays
    global birthday_list
    global page

    formatted_list = discord.Embed(
        title='Birthdays',
        color=discord.Color.blue()
    )

    for i in range(min(len(birthday_list) - page[0] * 10, 10)):
        print(page[0])
        i += page[0] * 10
        temp_birthday = birthday_list[i].split("|")
        birthdate = temp_birthday[1].split('/')
        prefix = birthdate[0]
        if prefix == '1':
            prefix += 'st'
        elif prefix == '2':
            prefix += 'nd'
        elif prefix == '3':
            prefix += 'rd'
        else:
            prefix += 'th'

        if len(birthdate) == 2:
            formatted_list.add_field(name='`' + str(i + 1) + '`' + "  ",
                                     value=calendar.month_name[int(birthdate[1])] + " *" + prefix + '*', inline=False)

        else:
            formatted_list.add_field(name='`' + str(i + 1) + '`' + "  ",
                                     value=temp_birthday[0] + " *" + calendar.month_name[int(birthdate[1])] + " " +
                                           prefix + birthdate[2] + '*',
                                     inline=False)
    return formatted_list


# The function to check if a added birthday is formatted right
def add_birthday(message, mention):
    global birthdays
    global birthday_list

    del message[0]
    if len(message) != 3 and len(message) != 4:
        return -1

    birth = ''

    if len(mention) != 1:
        mention = ''
    else:
        mention = mention[0].id

    name = message[0] + " " + message[1]
    given_date = message[2].split("/")

    if len(given_date) > 3 or len(given_date) < 2:
        return 0

    for i in range(len(given_date)):
        if not given_date[i].isnumeric():
            return 1

        if len(given_date[i]) != 2 and i != 2:
            return 2

        if len(given_date[i]) != 4 and i == 2:
            return 3

        birth = given_date[0] + '/' + given_date[1]

        if len(given_date) == 3:
            birth += '/' + given_date[2]

    print(name, birth, mention)
    return [name, birth, mention]


# To print to the console when the bot is ready
@client.event
async def on_ready():
    print('yes')
    # Starts the check_loop
    check_birthdays.start()


# Prints the current state of birthday list when it shuts
@client.command()
@commands.has_permissions(manage_roles=True)
async def grab_birthdays(ctx):
    global birthdays

    birthdays = open("Birthdays.txt", "r")
    await ctx.send(birthdays.read())


@client.command(aliases=['Ping'])
async def ping(ctx):
    await ctx.send(f'Pong is {round(client.latency * 1000)}ms')


# Note to self, change to manage messages
@client.command(aliases=['Prune', 'Purge', 'purge'])
@commands.has_permissions(manage_roles=True)
async def prune(ctx):
    await ctx.send(f'Pruning {ctx.message.content.split(" ")[1]} messages')
    await ctx.channel.purge(limit=int(ctx.message.content.split(" ")[1]))


@client.command()
async def help(ctx):
    help_embed = discord.Embed(
        title='Bot Commands',
        description='>>> These commands are weird man',
        colour=discord.Color.orange()
    )

    help_embed.add_field(name='Add [name] [date] [user]',
                         value="You can have either 2 or 3 parameters. First you need name, `First Name` "
                               "`Last Name` seperated with a space. Then birthday in either `dd/mm` or `dd/mm/yyyy`. "
                               "Then if applicable, `mention` the user. Members will need a vote to add",
                         inline=False)

    help_embed.add_field(name='Ping', value="The latency of the bot", inline=False)

    help_embed.add_field(name='SetChannel', value="Sets the channel the bot sends to. Short form is `sc`", inline=False)

    help_embed.add_field(name='BirthdayList', value="Returns the list of all birthdays. Short form is `bl`",
                         inline=False)

    help_embed.add_field(name='Del [n]', value="Deletes the `n`'th birthday. Needs manage role perms", inline=False)

    help_embed.add_field(name='NextBirthday',
                         value="Tells you the next birthday. Short form is `nb`", inline=False)

    help_embed.add_field(name='Prune [n]',
                         value="Prunes the past `n` messages", inline=False)

    await ctx.send(embed=help_embed)


@client.command(aliases=['setchannel', 'setChannel', 'Setchannel', 'SetChannel', 'sc'])
@commands.has_permissions(manage_roles=True)
async def set_channel(ctx):
    global channel
    rewrite = open('Channel.txt', 'w')
    rewrite.write(str(ctx.message.channel.id))
    channel = open('Channel.txt', 'r')

    await ctx.send('Wow you did it, how many tries did it take')


@client.command(aliases=['nb', 'nB', 'nextBirthday',
                         'nextbirthday'])
async def next_birthday(ctx):
    global birthday_list

    birthdate = birthday_list[0].split('|')[1].split('/')
    prefix = birthdate[0]
    if prefix == '1':
        prefix += 'st'
    elif prefix == '2':
        prefix += 'nd'
    elif prefix == '3':
        prefix += 'rd'
    else:
        prefix += 'th'

    name = birthday_list[0].split('|')[0]
    await ctx.send(f"```pl\n BIRTHDAY\n\n The next birthday is %s's on " % name +
                   calendar.month_name[int(birthdate[1])] + " " + prefix + '```')


@client.command(aliases=['today', 'td', 't', 'Today'])
async def date(ctx):
    eastern = pytz.timezone('US/Eastern')
    today = datetime.now(eastern)

    await ctx.send(f"```pl\n DATE\n\n Today is " + today.strftime('%A %B %d') + '```')


# Only mod's can add a birthday straight up, members go through a different process
@client.command()
@commands.has_permissions(manage_roles=True)
async def add(ctx):
    # The birthday file and list
    global birthdays
    global birthday_list

    # The message format and the output of the function
    message = ctx.message.content.split(" ")
    mentions = ctx.message.mentions
    if len(mentions) > 1:
        await ctx.send('why two mentions')
        return
    output = add_birthday(message, mentions)

    print(output)
    # Send messages based on what error
    if output == -1:
        await ctx.send('The format of the birthday is incorrect')

    elif output == 0:
        await ctx.send('The date is formatted incorrectly')

    elif output == 1:
        await ctx.send('The date contains a string')

    elif output == 2:
        await ctx.send('Make sure your single digit months and dates use 0')

    elif output == 3:
        await ctx.send('Make sure your year is 4 digits long')

    # Adds the birthday if no errors
    else:
        # Switches file mode to append
        birthdays = open('Birthdays.txt', 'a')

        birthdays.write('\n' + output[0] + '|' + output[1] + '|' + str(output[2]))

        birthdays = open('Birthdays.txt', 'r')
        birthday_list = birthdays.read().split("\n")

        sort_birthday()

        await ctx.send('Birthday successfully added!')


# If the user adding the birthday is not a mod or higher
# This works because if the member was not a mod, the check would send an error
@add.error
async def add_error(ctx, error):
    print(error)
    # Checking if the error was a permission error
    if isinstance(error, discord.ext.commands.CheckFailure):

        # The birthday as well as the variable to keep track of the votes
        global birthdays
        global birthday_list
        global current_birthday

        # Same stuff as above, formatting the message and getting the output of the function
        message = ctx.message.content.split(" ")
        mentions = ctx.message.mentions

        if len(mentions) > 1:
            await ctx.send('why two mentions')
            return

        output = add_birthday(message, mentions)

        # Same stuff, outputs if there's an error
        if output == -1:
            await ctx.send('The format of the birthday is incorrect')

        elif output == 0:
            await ctx.send('The date is formatted incorrectly')

        elif output == 1:
            await ctx.send('The date contains a string')

        elif output == 2:
            await ctx.send('Make sure your single digit months and dates use 0')

        elif output == 3:
            await ctx.send('Make sure your year is 4 digits long')

        # This is different, it now sends a message where you either need 8 people to vote, or a mod to vote
        else:
            # Dhan, change this to an embed please
            sent_message = discord.Embed(
                description='`Get a moderator or higher power to vote this birthday in, or get 2 people to vote.`',
                colour=discord.Color.red())

            message = await ctx.send(embed=sent_message)

            emote = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emote)

            # Sets up the vote variable
            current_birthday = [output[0], output[1], output[2], message, 0]


# This function sends a list of all documented birthdays
@client.command(aliases=['birthdaylist', 'birthdayList', 'BirthdayList', 'Birthdaylist', 'bl', 'b_l'])
async def birthdays_list(ctx):
    global page
    page = [0, 0, 0, False]

    formatted_list = birthday_list_embed()
    message = await ctx.send(embed=formatted_list)

    page[1] = message
    page[2] = ctx.message.author
    await message.add_reaction('⬅️')
    await message.add_reaction('⏹️')
    await message.add_reaction('➡️')


# When a reaction is added
@client.event
async def on_reaction_add(reaction, user: discord.Member = None):
    global current_birthday
    global birthdays
    global birthday_list
    global page

    # If it is not voting time, then it returns
    if current_birthday[2] == 0 and page[1] == 0:
        return

    if user.id == 723970312190033991:
        return
    if reaction.message == page[1] and reaction.emoji == '⏹️' and user == page[2]:
        page[3] = True

    # If the reaction is right and it is on the birthday list then we swap
    if reaction.message == page[1] and reaction.emoji == '➡️' or reaction.message == page[1] and reaction.emoji == '⬅️':
        await reaction.message.remove_reaction(reaction.emoji, user)
        print(page[3])
        if page[3]:
            return
        if reaction.emoji == '➡️':
            if not page[0] * 10 >= len(birthday_list) - 10:
                page[0] += 1
            else:
                return

        if reaction.emoji == '⬅️':
            if not page[0] * 10 == 0:
                page[0] -= 1
            else:
                return

        formatted_list = birthday_list_embed()
        await reaction.message.edit(embed=formatted_list)

    # If the reaction is a thumbs up and also on the message to vote, it adds a vote and checks if its an mod who voted
    if reaction.message == current_birthday[3] and reaction.emoji == '\N{THUMBS UP SIGN}':

        # Adds one to the people who have voted
        current_birthday[4] += 1

        # Checks if the user has mod roles
        if user.guild_permissions.manage_roles and user is not None:
            # Adds to the birthday file and resets the voting variable
            # Switches file mode to append
            birthdays = open('Birthdays.txt', 'a')

            birthdays.write('\n' + current_birthday[0] + '|' + current_birthday[1] + '|' + current_birthday[2])
            birthdays = open('Birthdays.txt', 'r')
            birthday_list = birthdays.read().split("\n")

            sort_birthday()

            await reaction.message.channel.send('Birthday successfully added!')
            current_birthday = ['', '', '', '', 0]

        # checks if enough people have voted
        elif current_birthday[4] >= 1:
            # Adds to the birthday file and resets the voting variable
            birthdays = open('Birthdays.txt', 'a')
            birthdays.write('\n' + current_birthday[0] + '|' + current_birthday[1] + '|' + current_birthday[2])
            birthdays = open('Birthdays.txt', 'r')
            birthday_list = birthdays.read().split("\n")

            sort_birthday()

            await reaction.message.channel.send('Birthday successfully added!')
            current_birthday = ['', '', '', '', 0]


@client.event
async def on_reaction_remove(reaction, user: discord.Member = None):
    global page

    if user.id == 723970312190033991:
        print(page[2])
        return

    if reaction.message == page[1] and reaction.emoji == '⏹️' and user == page[2]:
        page[3] = False


@client.command(aliases=['Delete', 'del', 'Del'])
@commands.has_permissions(manage_roles=True)
async def delete(ctx):
    global birthdays
    global birthday_list

    # Checks if the second part is actually a integer
    if not ctx.message.content.split(" ")[1].isnumeric():
        await ctx.send("Bruh")
        return

    # Finds the number and sets up the file for writing
    del_n = int(ctx.message.content.split(" ")[1])

    deleted = delete_n(del_n)

    birthdays = open('Birthdays.txt', 'r')
    birthday_list = birthdays.read().split('\n')
    await ctx.send('Nice, you deleted ' + deleted.split("|")[0] + "'s birthday")


@tasks.loop(minutes=1)
async def check_birthdays():
    global birthdays
    global birthday_list
    global channel

    eastern = pytz.timezone('US/Eastern')
    today = datetime.now(eastern)

    global birthdays

    channel = open('Channel.txt', 'r')
    channel_id = channel.read()
    if channel_id == '':
        return

    messages = await client.get_channel(int(channel_id)).history(limit=20).flatten()
    for message in messages:
        if message.author.id == 723970312190033991:
            if message.created_at.strftime('%A %B %d') == today.strftime('%A %B %d'):
                return

    sort_birthday()

    birthdays = open("Birthdays.txt", "r")
    birthday_list = birthdays.read().split('\n')

    for i in range(len(birthday_list)):
        birthdate = birthday_list[i].split('|')[1].split("/")

        if birthdate[0] == today.strftime('%d') and birthdate[1] == today.strftime('%m') and len(birthdate) == 3:
            age = int(today.strftime('%Y')) - int(birthdate[2])

            birthday_embed = discord.Embed(
                title='Birthday!!!',
                colour=discord.Color.purple(),
                description="__It's " + birthday_list[0].split('|')[0] + "'s Birthday!!__ \n" +
                            "_They are " + str(round(age * 76 / 64)) + "% dead_",
            )

            file = discord.File("Deaths/Hangman" + str(round(age * 76 / 64)) + '.png',
                                filename="Hangman" + str(round(age * 76 / 64)) + ".png")

            birthday_embed.set_image(
                url="attachment://Hangman" + str(round(age * 76 / 64)) + ".png"
            )

            birthday_embed.set_footer(text='They are ' + str(age) + ' now')

            chin = client.get_channel(int(channel_id))

            await chin.send(file=file, embed=birthday_embed)

            switch = delete_n(1)
            birthdays.write('\n' + switch)
            if birthday_list[0].split('|')[2] != '':
                mention_id = birthday_list[0].split('|')[2]

                mentioned_message = '>>> IT IS YOUR BIRTHDAY <@%s>' % mention_id

                await chin.send(mentioned_message)

            birthdays = open('Birthdays.txt', 'r')
            birthday_list = birthdays.read().split('\n')
        else:
            break


client.run(Token)
