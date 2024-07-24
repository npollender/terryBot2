#daily happy birthday messages
hbd_messages = [
  'Happy birthday Terry!'
  'it is terrys birthday my dudes',
  'Happy terry womb exiting day',
  'HBD Terrance!!!',
  'TERRY BIRD DAY CELEBRATION',
  'It is with great pleasure that I announce the day of birth of Terrance Ratigan.',
  'terry terry terry terry terry terry terry terry terry terry'
  'there arent any special events today... lmao sike its terrys bday bash!!!'
]

#happy birthday replies
hbd_replies = [
  'yo thats what im saying!',
  'fr fr happy birthday terrrrryyyy!!!!',
  'this is pretty true',
  'OMG YES HBD TERRANCE',
  'aaayyyyy lets gooooo',
  'happy birf day tewwy',
  'ladies and gentlemen, it is with great pleasure to inform you that it is terrys birthday',
  'me when its terrys birthday',
  'aka essence reaver tryndamere appreciation day',
  'a birthday a day keeps the dogtor away',
  'nice',
  'hApPy BiRtHdAy TeRrY',
  'gimornous birthday time mhm',
  'happy michigan birthday*',
  'cap',
  'imagine not having a birthday today lmaooooooooo'
]

#statuses
main_status = '>info | '
hbd_statuses = [
  'Happy birthday Terry!',
  'Terry womb exiting day',
  'I love Terry',
  '10/10 would hbd Terry again',
  'H B D T E R R Y'
]
standard_statuses = [
  'ginemenasaurus',
  'whatever you say',
  'gigantasourus',
  'gimenis-ba-manmoris',
  'symenaf morf',
  'gigananorstis',
  'mmhm',
  'gimornis'
]

#rude_replies
rude_replies = [
  'who asked?',
  'any askers?',
  'nobody asked terry',
  'me when I didnt ask'
]

#on_typing replies
on_typing_replies = [
  'shut up terry'
  'stop typing terry'
  'dont even think about sending that message terry, no one cares'
]

#on_voice_state_update messages
on_voice_messages = [
  'look who it is',
  'oh no, not this guy',
  'the birthday boy is back in town!!!',
  'hey guys, terry just joined the call fyi',
  'it is terry my dudes'
]

#on_voice_state_update audio paths
on_voice_audio_paths = [

]

#various single use messages
self_hbd = 'Why are you wishing yourself a happy birthday lmao?'
reply_prio = 'You don\'t know what prio is.'

#command messages
cmd_info = 'I\'m HBDTerryBot, I have been programmed to wish our wonderful Terry a happy birthday every day throughout the month of August! I also have an unexplainably conflicting relationship with Terry which is why I also find pleasure in insulting him.'
response_error = 'Sorry, there was an issue retrieving the insiprational quote.'
session_error = 'Sorry, there is an issue with Inspirobot.'
busy = 'Slow down, I\'m busy.'

#gif urls
gif_urls = [
  
]
alternate_case_url = 'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZjAwdXg1aWFyYmJtN3pqanR6ZWt6bjdsNGx4bnM5OXhqZmZ5dDY4NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QUXYcgCwvCm4cKcrI3/giphy.gif'

#alternate uppercase & lowercase for msg
def alternate_case(msg):
  result = []
  toggle = False #f = lower, t = upper

  for char in msg:
    if char.isalpha():
      if toggle:
        result.append(char.upper())
      else:
        result.append(char.lower())
      toggle = not toggle
    else:
      result.append(char)

  return ''.join(result)