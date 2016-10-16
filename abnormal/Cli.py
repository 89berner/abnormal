import Queue
import threading
import time

class ThreadReplay(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url,observer) = self.queue.get()
            print "Performing action click for %s in url %s" % (observer.ip,url)
            addr = observer.address_map[url]
            addr.perform_action('click')
            self.queue.task_done()

class Cli:
    def __init__(self, ab):
        self.ab = ab
        self.close = ['quit','q','close','exit']
        self.back  = ['back']

    def start(self):
      prompt = "> "
      print "Do you want to replay from javascript (js) or image (img) input?"
      while (1):
        answ = raw_input(prompt).strip()
        if answ in self.close:
          print "Bye!"
          break
        elif answ == "js" or answ == "javascript":
          status = self.js_prompt()
          if not status:
            return
        elif answ == 'img' or answ == 'image':
          status = self.img_prompt()
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
      print "2) Image console"
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

    def img_prompt(self):
      prompt = 'img>'
      while(1):
        print "Choose the md5 of the image you want to replay"
        answ = raw_input(prompt)

        if answ in self.close:
          print "Bye!"
          return 0
        elif answ in self.back:
          break
        elif not self.ab.check_img(answ):
          print "No observer has an image which md5 is %s..." % answ
          time.sleep(1)
          break
        else:
          observers = self.ab.get_img_observers(answ)
          print "We have %s observers" % len(observers)
          self.replay('img',observers)

    def replay(self,path,observers):
      prompt = "%s>replay>" % path
      while(1):
        print "Choose action to replay"
        print "1) Perform click"
        answ = raw_input(prompt).strip()
        print "You chose %s" % answ
        if answ in self.close:
          print "Bye!"
          return 0
        elif answ in self.back:
          break
        elif answ == "1":
          queue = Queue.Queue()
          for i in range(10):
              t = ThreadReplay(queue)
              t.setDaemon(True)
              t.start()

          for observer in observers:
              queue.put(observer)

          queue.join()            
        else:
          print "Unknown option %s" % answ