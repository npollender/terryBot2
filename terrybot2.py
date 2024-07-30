#packages
import nextcord
import asyncio
import random
import requests
import re
from datetime import datetime, timedelta
from nextcord.ext import commands, tasks

#local
import config
import messages

intents = nextcord.Intents.default()
intents.message_content = True
intents.typing = True
intents.members = True

bot = commands.Bot(command_prefix='>', intents=intents)

#some actions have a cooldown so they do not happen too often
cd_ontype_users = set()
cd_onvoice_users = set()
cd_reply_users = set()
cd_d20_users = set()
cd_d20_crit = False

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

  channel = bot.get_channel(config.text_main)
  if channel:
    #only send hbd messages during the month of august
    if target_time.month == 8:
      await channel.send(random.choice(messages.hbd_messages))
      cd_reply_users.clear() #reply cd reset after daily hbd message is sent
    #when december - display xmas inspirobot quote
    elif target_time.month == 12:
      response = requests.get('https://inspirobot.me/api?generate=true&season=xmas')
      if response.status_code == 200:
        await channel.send(response.content.decode('utf-8'))
      else:
        print(f'Inspirobot error: status code = {response.status_code}')
    #when other months - display standard quote
    else:
      response = requests.get('https://inspirobot.me/api?generate=true')
      if response.status_code == 200:
        await channel.send(response.content.decode('utf-8'))
      else:
        print(f'Inspirobot error: status code = {response.status_code}')
    cd_d20_users.clear() #reset d20 cd after daily msg

#randomly change bot status every 15 minutes
@tasks.loop(minutes=15)
async def change_status():
  now = datetime.now()
  if now.month == 8:
    new_status = f'{messages.main_status}{random.choice(messages.hbd_statuses)}'
  else:
    new_status = f'{messages.main_status}{random.choice(messages.standard_statuses)}'
  await bot.change_presence(activity=nextcord.CustomActivity(name=new_status))

##################
# --- EVENTS --- #
##################

#behavior for various messages
@bot.event
async def on_message(message):
  #ignore any message sent by the bot itself
  if message.author == bot.user:
    return
  
  now = datetime.now()

  #react upon message in main text channel
  if message.channel.id == config.text_main:
    if re.search(r'\b(?:happy birthday|hbd)\b.*\bterry\b', message.content, re.IGNORECASE) and now.month == 8:
      if message.author.id == config.user_terry:
        await message.reply(messages.self_hbd)
      elif message.author.id not in cd_reply_users:
        await message.reply(random.choice(messages.hbd_replies))
        cd_reply_users.add(message.author.id) #only reply to each user once
    elif message.author.id == config.user_terry and len(message.content) > 20:
      alt_chance = 1 / (len(messages.rude_replies) + 1)
      if random.random() < alt_chance:
        await message.reply(f'{messages.alternate_case(message.content)}')
        await message.channel.send(f'{messages.alternate_case_url}')
      else:
        await message.reply(random.choice(messages.rude_replies))
    elif re.search(r'\b(?:prio|priority)\b', message.content, re.IGNORECASE):
      await message.reply(messages.reply_prio)

  await bot.process_commands(message)

#behavior for when someone is typing a message in main text channel - 30min cd
@bot.event
async def on_typing(channel, user, when):
  if user.id == config.user_terry and user.id not in cd_ontype_users:
    cd_ontype_users.add(user.id)
    if random.random() < 0.1:
      await channel.send(random.choice(messages.on_typing_replies))
    await asyncio.sleep(30 * 60)
    cd_ontype_users.remove(user.id)

#behavior for when someone joins a voice channel - 30min cd
@bot.event
async def on_voice_state_update(member, before, after, volume: float = 0.2):
  now = datetime.now()
  if member.id == config.user_terry and before.channel is None and after.channel.id == config.voice_main and member.id not in cd_onvoice_users:
    cd_onvoice_users.add(member.id)
    if random.random() < 0.2 and now.month == 8:
      await asyncio.sleep(5) #wait 5 seconds in case of initial connection delays
      await play_audio(after.channel, random.choice(messages.on_voice_audio_paths), volume)
    else:
      text_channel = bot.get_channel(config.text_main)
      await text_channel.send(random.choice(messages.on_voice_messages))
    await asyncio.sleep(30 * 60)
    cd_onvoice_users.remove(member.id)
  elif member.id == config.user_terry and before.channel is None:
    print('Do nothing, just avoids error log.')
  elif member.id == config.user_terry and before.channel.id == config.voice_afk and after.channel.id == config.voice_main:
    print('here')
    if random.random() < 0.1:
      text_channel = bot.get_channel(config.text_main)
      await text_channel.send(messages.kick)
      await play_audio(after.channel, messages.on_voice_outro, volume)
      await asyncio.sleep(19)
      await member.move_to(config.voice_afk)

####################
# --- COMMANDS --- #
####################

#command info
@bot.command()
async def cmd(ctx):
  await ctx.send(messages.cmd_commands)

#bot info
@bot.command()
async def info(ctx):
  await ctx.send(messages.cmd_info)

#play audio from InspiroBot
@bot.command()
async def inspireme(ctx, volume: float = 0.2):
  if not ctx.voice_client:
    session = requests.get('https://inspirobot.me/api?getSessionID=1')
    if session.status_code == 200:
      response = requests.get(f'https://inspirobot.me/api?generateFlow=1&sessionID={session.content}')
      if response.status_code == 200:
        data = response.json()
        media = data.get('mp3', None)
        await play_audio(ctx.author.voice.channel, media, volume)
      else:
        await ctx.send(messages.response_error)
    else:
      await ctx.send(messages.session_error)
  else:
    await ctx.send(messages.busy)

#debug - force daily quote
@bot.command()
async def quote(ctx):
  if ctx.author.id == config.user_nick:
    response = requests.get('https://inspirobot.me/api?generate=true')
    if response.status_code == 200:
      await ctx.send(response.content.decode('utf-8'))

@bot.command()
async def force_clear(ctx):
  if ctx.author.id == config.user_nick:
    cd_reply_users.clear()
    cd_ontype_users.clear()
    cd_onvoice_users.clear()
    cd_d20_users.clear()
    await ctx.send('Cooldown sets cleared.')

@bot.command()
async def d20(ctx):
  if ctx.author.id == config.user_terry and ctx.author.id not in cd_d20_users:
    await ctx.send(f'🎲 You rolled a 1! Better luck next time.')
  elif ctx.author.id not in cd_d20_users:
    roll = random.randint(1, 20)
    await ctx.send(f'🎲 You rolled a {roll}!')
    member = ctx.guild.get_member(config.user_terry)
    if roll == 20 and member.voice and not cd_d20_crit:
      await ctx.send('Critical hit! You have successfully kicked Terry from the call.')
      await member.move_to(None)
      cd_d20_crit = True
    elif roll == 20 and not member.voice:
      await ctx.send('Critical hit! However, the special condition was not met...')
    elif roll == 20 and cd_d20_crit:
      await ctx.send('Critical hit! But I don\'t feel like doing anything about it.')
      if random.random() < 0.25:
        cd_d20_crit = False
  else:
    await ctx.send('Sorry, you already rolled today.')
  cd_d20_users.add(ctx.author.id)

@bot.command()
async def force_d20_flag(ctx, flag: bool):
  if ctx.author.id == config.user_nick:
    cd_d20_crit = flag
    
#####################
# --- FUNCTIONS --- #
#####################

#join call, play audio, leave call
async def play_audio(channel, media, volume):
  voice_channel = channel
  voice_client = await voice_channel.connect()

  audio_source = nextcord.FFmpegPCMAudio(media)
  audio_source = nextcord.PCMVolumeTransformer(audio_source, volume=volume)

  async def after_playing(error):
    try:
      co_ro = voice_client.disconnect()
      asyncio.run_coroutine_threadsafe(co_ro, bot.loop)
    except Exception as e:
      print(f'Error disconnecting: {e}')

  if not voice_client.is_playing():
    voice_client.play(audio_source, after=after_playing)

###############
# --- RUN --- #
###############

bot.run(config.token)