def js_prompt(ab):
  print "Choose the JS variable, use name=value for a particular value"
  answ = raw_input(prompt)
  name  = answ.split("=")[0]
  if not ab.check_var(name):
    print "No observer has %s..." % answ
    sleep(3)
    return
  else:
    if "=" in answ:
      value = answ.split("=")[1]
      ab.get_observers(answ,value)
    else:
      ab.get_observers(answ)

def start_cli(ab):
  prompt = '> '
  while (1):
    answ = raw_input(prompt)
    if answ == "quit" or answ == "q" or answ == "close" or answ == "exit":
      print "Bye!"
      break
    elif answ == "js" or answ == "javascript":
      js_prompt(ab)