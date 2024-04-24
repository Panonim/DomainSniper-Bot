import discord
import os
import json
import requests
from discord.ext import tasks

intents = discord.Intents.default()
intents.messages = True

DISCORD_TOKEN = os.environ['BOT_TOKEN']
API_KEY = os.environ['WHOIS_API']
DOMAIN_NAME = 'YOUR DOMAIN HERE'
USER_ID = YOUR USER ID HERE
CHANNEL_ID = YOUR CHANNEL ID HERE

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    user = client.get_user(USER_ID)
    if user:
        await user.send(
            "Whois information will be sent to the specified channel every day.")
    send_whois_info.start()  

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!whois'):
        if isinstance(message.channel, discord.DMChannel): 
            await send_whois_info(destination=message.channel)
        else:
            await send_whois_info(destination=message.channel)

@tasks.loop(hours=24) # Schedule to run every 24 hours (Default, change to your own prefers.) 
async def send_whois_info(destination=None):
    if destination is None:
        destination = client.get_channel(CHANNEL_ID)
    if destination:
        with open('settings.json') as settings_file:
            settings = json.load(settings_file)
        selected_fields = settings.get("selected_fields", [])  
        whois_info = await get_whois_info(DOMAIN_NAME, selected_fields)
        if whois_info:
            embed = discord.Embed(title=f"Whois Info for {DOMAIN_NAME}",
                                  description="",
                                  color=0x00ff00)
            for field, value in whois_info.items():
                print(field, value)
                embed.add_field(name=field, value=value, inline=True)
            await destination.send(embed=embed)

async def get_whois_info(domain, selected_fields):
    url = f'https://api.ip2whois.com/v2?key={API_KEY}&domain={domain}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result = {}
        for field in selected_fields:
            if field in data:
                result[field] = data[field]
        return result
    except requests.exceptions.RequestException as err:
        print(f'Error while fetching whois info: {err}')
    except KeyError as err:
        print(f'Missing key in whois info: {err}')

send_whois_info.before_loop(client.wait_until_ready) 
client.run(DISCORD_TOKEN)

