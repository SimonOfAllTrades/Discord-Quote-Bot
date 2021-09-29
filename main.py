import string
import discord
import random
import os
from discord.enums import ChannelType
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.none()
intents.reactions = True
intents.members = True
intents.guilds = True

TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = discord.Intents.all()
client = discord.Client(intents=intents)

members = []
channels = []
quotes_channels = []
messages = []
guild = None

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


#TODO moves everything into a function
@client.event
async def on_ready():
    global messages
    print("We have logged in as {}".format(client.user))

    for g in client.guilds:
        if g.id == GUILD_ID:
            guild = g
            break
    
    if guild:
        for member in guild.members:
            members.append(member)
    else:
        print("broken")

    #TODO change this to be passed as some sort of variable
    channels = guild.text_channels
    for channel in channels:
        if channel.id == 892641837112770591:
            quotes_channels.append(channel)

    for channel in quotes_channels:
        messages += await channel.history(limit=200).flatten()
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.channel.id == 892612985481203725:
        for member in members:
            member_tag = "<@!{}>".format(member.id)
            if member_tag in message.content:
                quote = pick_random_quote(member.id)
                user_name = member.name
                quote = "{}: {}".format(user_name, quote)
                await message.channel.send(quote)

client.run(TOKEN)
