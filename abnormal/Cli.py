import time

class Cli:
    def __init__(self, ab):
        self.ab = ab
        self.close = ['quit','q','close','exit']
        self.back  = ['back']

    def start(self):
      prompt = "> "
      while (1):
        answ = raw_input(prompt)
        if answ in self.close:
          print "Bye!"
          break
        elif answ == "js" or answ == "javascript":
          status = self.js_prompt()
          if not status:
            return
        else:
          print "Unknown option: %s" % answ

    def select_target(self):
      prompt = "> "

      num = 0
      result = {}
      for target in self.ab.targets:
        print "%s) %s" % (num,target)
        num += 1
        result[num] = target

      answ = raw_input(prompt)
      if answ in self.close:
        print "Bye!"
        return 0
      elif answ not in result:
        print "Going back"
        time.sleep(1)
        return 1
      else:
        return self.select_url(result[answ])

    def select_url(self,target_name): #Could allow multiple choices
      prompt = "%s> " % target_name
      urls = self.ab.targets[target_name].urls
      for i, url in enumerate(urls):
          print "%s) %s" % (i,url)
      print "%s) All urls" % len(urls)
      answ = raw_input(prompt)
      if answ in self.close:
        print "Bye!"
        return 0
      elif urls[answ] not in urls:
        print "Going back"
        time.sleep(1)
        return 1
      else:
        if answ == len(urls): #Chose all
          self.options_prompt(target_name,urls)
        else:
          self.options_prompt(target_name,[urls[answ]])

    def options_prompt(target_name,urls):
      prompt = "%s/%s> " % (urls.join(","),target_name)
      print "1) Javascript console"
      answ = raw_input(prompt)
      if answ in self.close:
        print "Bye!"
        return 0
      elif answ not in [1]:
        print "Going back"
        time.sleep(1)
        return 1
      elif answ == 1:
        self.js_prompt(target_name,urls)

    def js_prompt(self):
      prompt = "js> "
      while(1):
        print "Choose the JS variable, use name=value for a particular value"
        answ = raw_input(prompt)

        name = answ
        if "=" in answ:
          name = answ.split("=")[0]

        if answ in self.close:
          print "Bye!"
          return 0
        elif answ in self.back:
          break
        elif not self.ab.check_var(name):
          print "No observer has %s..." % answ
          time.sleep(1)
          break
        else:
          if "=" in answ:
            value = answ.split("=")[1]
            print self.ab.get_var_observers(name,value)
          else:
            print self.ab.get_var_observers(name)
      return 1
