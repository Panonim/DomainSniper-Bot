import discord
import os
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
    send_whois_info.start()  # Start the task loop

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!whois'):
        if isinstance(message.channel, discord.DMChannel):  # Check if message is in DM
            await send_whois_info(destination=message.channel)
        else:
            await send_whois_info(destination=message.channel)

@tasks.loop(hours=24)  # Schedule to run every 24 hours
async def send_whois_info(destination=None):  # Updated function definition to accept an optional argument
    if destination is None:
        destination = client.get_channel(CHANNEL_ID)
    if destination:
        whois_info = await get_whois_info(DOMAIN_NAME)
        if whois_info:
            embed = discord.Embed(title=f"Whois Info for {DOMAIN_NAME}",
                                  description="",
                                  color=0x00ff00)
            embed.add_field(name="domain", value=whois_info['domain'], inline=True)
            embed.add_field(name="domain_age",
                            value=whois_info['domain_age'],
                            inline=True)
            embed.add_field(name="expire_date",
                            value=whois_info['expire_date'],
                            inline=True)
            embed.add_field(name="update_date",
                            value=whois_info['update_date'],
                            inline=True)
            await destination.send(embed=embed)

async def get_whois_info(domain):
    url = f'https://api.ip2whois.com/v2?key={API_KEY}&domain={domain}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            'domain': data['domain'],
            'domain_age': data['domain_age'],
            'expire_date': data['expire_date'],
            'update_date': data['update_date']
        }
    except requests.exceptions.RequestException as err:
        print(f'Error while fetching whois info: {err}')
    except KeyError as err:
        print(f'Missing key in whois info: {err}')

send_whois_info.before_loop(client.wait_until_ready) 
client.run(DISCORD_TOKEN)
