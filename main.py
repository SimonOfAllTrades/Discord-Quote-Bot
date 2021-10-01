import discord
import random
import os
from discord.enums import ChannelType
from discord.ext import commands
from dotenv import load_dotenv


################ INITIALIZATION ################

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix='!')

members = set()
text_channels = set()
quotes_channels = set()
messages = []
guild = None

################################################


def pick_random_quote(id):
    global messages
    valid_messages = []
    string_id = "<@!{}>".format(id)
    for message in messages:
        if string_id in message.content:
            valid_messages.append(message)
    
    quote = random.choice(valid_messages).content
    quote = quote.replace(string_id, "")
    return quote


################ HELPER FUNCTIONS ################

def get_messages(channel):
    return channel.history(limit=200).flatten()

def get_channel(channel_id):
    return client.get_channel(int(channel_id))

def add_quote_channel(channel_id):
    quotes_channels.add(int(channel_id))

def add_text_channel(channel_id):
    text_channels.add(int(channel_id))

#TODO clear all messages then retry to get messages
def remove_quote_channel(channel_id):
    quotes_channels.discard(int(channel_id))

def remove_text_channel(channel_id):
    text_channels.discard(int(channel_id))

def get_channel_name(channel_id):
    return get_channel(int(channel_id))

################################################


#TODO moves everything into a function
@client.event
async def on_ready():
    global messages
    print("Quote bot is now ready to quote")

    for g in client.guilds:
        if g.id == GUILD_ID:
            guild = g
            break
    
    if guild:
        for member in guild.members:
            members.add(member)
    else:
        print("No guild found!")


@client.event
async def on_message(message):
    global messages
    global text_channels
    global quotes_channels
    # Prevent infinite recursion causing our doom!
    if message.author == client.user:
        return

    current_channel = message.channel

#TODO change this to be actual commands
################ COMMANDS ################

    command = message.content

    if command.startswith("!add_quote_channel "):
        channel_ids = message.content.split(" ")
        for channel_id in channel_ids[1:]:
            # So this will fail if the user inputs \ since the string doesn't escape it properly
            if channel_id.isdigit and get_channel(channel_id):
                add_quote_channel(channel_id)
                messages += await get_messages(get_channel(channel_id))
        return

    if command.startswith("!add_text_channel "):
        channel_ids = message.content.split(" ")
        for channel_id in channel_ids[1:]:
            if channel_id.isdigit and get_channel(channel_id):
                add_text_channel(channel_id)
        return

    if command.startswith("!remove_quote_channel "):
        channel_ids = message.content.split(" ")
        for channel_id in channel_ids[1:]:
            if channel_id.isdigit and get_channel(channel_id):
                remove_quote_channel(channel_id)
        return

    if command.startswith("!remove_text_channel "):
        channel_ids = message.content.split(" ")
        for channel_id in channel_ids[1:]:
            if channel_id.isdigit() and get_channel(channel_id):
                remove_text_channel(channel_id)
        return

    if command.startswith("!list_text_channels"):
        await current_channel.send(
            "**Text channels:** " + ','.join(map(str, [get_channel(text_channel) for text_channel in text_channels])) if text_channels else
            "There are no text channels"
        )
        return

    if command.startswith("!list_quote_channels"):
        await current_channel.send(
            "**Quotes channels:** " + ','.join(map(str, [get_channel(quotes_channel) for quotes_channel in quotes_channels])) if quotes_channels else
            "There are no quotes channels" #ternary operator here
        )
        return
    
################################################

    if message.channel.id in text_channels:
        for member in members:
            member_tag = "<@!{}>".format(member.id)
            if member_tag in message.content:
                quote = pick_random_quote(member.id)
                user_name = member.name
                quote = "{}: {}".format(user_name, quote)
                await current_channel.send(quote)

client.run(TOKEN)
