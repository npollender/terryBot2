#packages
import nextcord
import asyncio
import random
import re
from datetime import datetime, timedelta
from nextcord.ext import commands, tasks

#local
import config
import messages

intents = nextcord.Intents.default()
intents.message_content = True
intents.typing = True

bot = commands.Bot(command_prefix='>', intents=intents)

#some actions have a cooldown so they do not happen too often
cd_ontype_users = set()
cd_onvoice_users = set()

################
# --- INIT --- #
################

#log successful login and start tasks
@bot.event
async def on_ready():
  print(f'Bot successfully logged in as {bot.user}')
  send_daily_hbd_message.start()
  change_status.start()

#################
# --- TASKS --- #
#################

#send daily happy birthday message to terry - but only in august
@tasks.loop(hours=24)
async def send_daily_hbd_message():
  await bot.wait_until_ready()
  now = datetime.now()
  target_time = datetime.combine(now.date(), datetime.strptime("10:00", "%H:%M").time())

  if now >= target_time:
    target_time += timedelta(days=1)

  wait_time = (target_time - now).total_seconds()
  print(f'HBD message successfully scheduled for {target_time}, in {wait_time} seconds.')
  await asyncio.sleep(wait_time)

  if datetime.now() == 8:
    channel = bot.get_channel(config.text_main)
    if channel:
      await channel.send(random.choice(messages.hbd_messages))

#randomly change bot status every 15 minutes
@tasks.loop(minutes=15)
async def change_status():
  new_status = random.choice(f'{messages.main_status}{messages.hbd_statuses}')
  await bot.change_presence(activity=nextcord.Game(name=new_status))

##################
# --- EVENTS --- #
##################

#behavior for various messages
@bot.event
async def on_message(message):
  #ignore any message sent by the bot itself
  if message.author == bot.user:
    return
  
  #react upon message in main text channel
  if message.channel.id == config.text_main:
    if re.search(r'\b(?:happy birthday|hbd)\b.*\bterry\b', message.content, re.IGNORECASE):
      if message.author == config.user_terry:
        await message.channel.reply(messages.self_hbd)
      else:
        await message.channel.reply(random.choice(messages.hbd_replies))
    elif message.author == config.user_terry and len(message.content) > 20:
      alt_chance = 1 / (len(messages.rude_replies) + 1)
      if random.random() < alt_chance:
        await message.channel.reply(f'{messages.alternate_case(message.content)}\n{messages.alternate_case_url}')
      else:
        await message.channel.reply(random.choice(messages.rude_replies))
    elif re.search(r'\b(?:prio|priority)\b', message.content, re.IGNORECASE):
      await message.channel.reply(messages.reply_prio)

  await bot.process_commands(message)

#behavior for when someone is typing a message in main text channel - 30min cd
@bot.event
async def on_typing(channel, user, when):
  if user.id == config.user_terry and user.id not in cd_ontype_users:
    cd_ontype_users.add(user.id)
    if random.random() < 0.1:
      await channel.send('MESSAGE') #TODO - add messages for on_typing replies
    await asyncio.sleep(30 * 60)
    cd_ontype_users.remove(user.id)

#behavior for when someone joins a voice channel - 30min cd
@bot.event
async def on_voice_state_update(member, before, after):
  if member.id == config.user_terry and before.channel is None and after.channel.id == config.voice_main and member.id not in cd_onvoice_users:
    cd_onvoice_users.add(member.id)
    text_channel = config.text_main
    await text_channel.send(random.choice(messages.on_voice_messages))
    await asyncio.sleep(30 * 60)
    cd_onvoice_users.remove(member.id)

####################
# --- COMMANDS --- #
####################

#bot info
@bot.command
async def info(ctx):
  await ctx.send(messages.cmd_info)

#list of *non-secret* commands
@bot.command
async def cmd(ctx):
  await ctx.send() #TODO - add list of commands to messages.py

#tmp - test if sound is played
@bot.command
async def tmp_play_sound(ctx):
  if ctx.author.voice:
    channel = ctx.author.voice.channel
    vc = await channel.connect()

    vc.play(nextcord.FFmpegPCMAudio('')) #TODO - add media folder with sounds/audio
    while vc.is_playing():
      nextcord.sleep(1)

    await vc.disconnect()

###############
# --- RUN --- #
###############

bot.run(config.token)