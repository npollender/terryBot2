#packages
import discord
import asyncio
import random
from datetime import datetime, timedelta

#local
import config
import messages

intents = discord.Intents.default()
intents.message_content = True
intents.typing = True

client = discord.Client(intents=intents)

#some actions have a cooldown so they do not happen too often
cd_ontype_users = set()

#send daily happy birthday message to terry - but only in august
async def send_daily_hbd_message():
  await client.wait_until_ready()
  channel = client.get_channel(config.text_main)

  while not client.is_closed():
    now = datetime.now()
    target_time = datetime.combine(now.date(), datetime.strptime("10:00", "%H:%M").time())
    
    if now >= target_time:
      target_time += timedelta(days=1)

    wait_time = (target_time - now).total_seconds()
    await asyncio.sleep(wait_time)
    if datetime.now().month == 8:
      await channel.send(random.choice(messages.hbd_messages))
    await asyncio.sleep(24 * 60 * 60)

#log successful login
@client.event
async def on_ready():
  print(f'Bot successfully logged in as {client.user}')

#behavior for various messages
@client.event
async def on_message(message):
  #ignore any message sent by the bot itself
  if message.author == client.user:
    return
  
  #react upon message in main text channel
  if message.channel.id == config.text_main:
    #TODO - add reactions to different messages - currently auto replies in alternating case ...
    await message.channel.send(messages.alternate_case(message.content))

@client.event
async def on_typing(channel, user, when):
  if user.id == config.user_terry and user.id not in cd_ontype_users:
    cd_ontype_users.add(user.id)
    if random.random() < 0.1:
      await channel.send('MESSAGE') #TODO - add messages for on_typing replies
    await asyncio.sleep(30 * 60)
    cd_ontype_users.remove(user.id)

client.loop.create_task(send_daily_hbd_message())

client.run(config.token)