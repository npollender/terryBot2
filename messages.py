#daily happy birthday messages
hbd_messages = [
  'Happy birthday Terry!'
  'it is terrys birthday my dudes',
  'terry womb exiting day',
  'HBD Terrance!!!',
  'TERRY BIRD DAY CELEBRATION',
  'It is with great pleasure that I announce the day of birth of Terrance Ratigan.',
  'terry terry terry terry terry terry terry terry terry terry'
  'there arent any special events today... lmao sike its terrys bday bash!!!'
]

#happy birthday replies
hbd_replies = [

]

#on_typing replies
on_typing_replies = [
  
]

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