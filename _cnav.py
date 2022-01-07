#!/usr/bin/python3
import nls_util as nut
notify = nut.notify
class Nav():
  def __init__(self):
    # ui/ux related
    self.opts = {
       "print_list_numbers":True
      ,"endless_search_mode":True
      ,"horizontal_split":False
      ,"main_w_title":"<cnav>"
      }
    self.keybinding_info = {
       "j, k":" -> Down, Up"
      ,"J, K":" -> PgDn, PgUp"
      ,"q"   :" -> quit and return selected item"
      }
    self.n_rec = 1
    self.break_list = ['q', 'h', 'l', '\n',"KEY_LEFT","KEY_RIGHT"]
    self.hnd_pointer = self.recursion_hndl
    self.logfile = "cnav.log"
    self.c = nut.Curses()
    self.mode = "normal"

  def log(self, log_data="", title=""):
    with (f := open(f"{self.logfile}", "a")):
      import time as t
      log_str = t.strftime("%m-%d %H:%M:%S") + f" - {title} >\n"
      log_str += log_data.replace("\n", "\n  ") + "\n\n"
      f.write(log_str)
      notify(f"log", "log written!")

  def navigate(self, iterable):
    c = self.c
    self.c.__enter__()

    if self.opts["horizontal_split"]:
      main_w_coords = ((c.max_y-2)//2,c.max_x-4,1,2)
      info_w_coords = ((c.max_y-2)//2,c.max_x-4,(c.max_y//2),2)
    else:
      main_w_coords = (c.max_y-2,(c.max_x-4)//2,1,2)
      info_w_coords = (c.max_y-2,(c.max_x-4)//2,1,(c.max_x//2))
    c.main_w = c.popup(title_str=self.opts["main_w_title"], coords=main_w_coords)
    c.info_w = c.popup(title_str="<info>",   coords=info_w_coords)

    self.history = [iterable]
    t = type(iterable)
    if t == dict:
      result = self.hnd_pointer(iterable)
    elif t == list:
      list_to_dict = {i : iterable[i] for i in range(len(iterable))}
      result = self.hnd_pointer(list_to_dict)
    elif t == str or t == int or t == bool:
      print("can't iterate anymore")
    self.c.__exit__(None,None,None)
    return result

  def recursion_hndl(self, iterable):
    self.history.append(iterable)
    while True:
      choice, info = self.get_choice(self.history[len(self.history)-1])
      if info["key"] == 'h' and len(self.history) > 1:
        self.history.pop()
        self.n_rec -= 1
        continue
      else:
        self.history.append(choice)
        self.n_rec += 1
      if (t := type(choice)) != dict and t != list or info["key"] == 'q':
        return self.history[len(self.history)-1]

  def get_choice(self, choices, preview:list=[]):
    c = self.c

    def ranger_help(help_dict, coords):
      help_w = c.popup("<help>", coords)
      y,x = help_w.getmaxyx()
      i = 0
      for k in help_dict:
        help_w.addstr(i+2,2,f"{k}\t{help_dict[k]}")
        if i == y-3: break
        i += 1
      help_w.refresh()
      help_w.getch()
      help_w.clear()

    def handle_line_input(key, line):
      if key == None: key = ""
      try:
        input_ord = ord(key)
      except TypeError:
        input_ord = None
      if input_ord == 127 or key == "KEY_BACKSPACE": #delete
        if len(line) == 0:
          self.mode = "normal"
        line = line[:-1]
      elif input_ord == 27: #escape
        line = ""
        self.mode = "normal"
      elif input_ord != None:
        line += key
      return key, line
                                
    choice = 0
    choices_ = choices
    self.len_resdir = len(choices)-1
    user_key = None 
    info = {}
    info.update(self.keybinding_info)
    info.update(self.opts)
    info["recursion_counter"] = self.n_rec
    offset = 0
    user_line = ""
    skip_input_once = False

    while True:
      keys = []
      # drawing is just implemented for dicts ...
      if type(choices) == list: 
        keys = [i  for i in range(len(choices))]
      else:
        keys = list(choices.keys())

      if choice > len(choices)-1:
        choice = offset = 0

      y,x = c.main_w.getmaxyx()
      screen_fit = y-3
      
      # draw main_w (main window)
      c.main_w.clear()
      for i in range(len(choices)):
        ioff = i + offset

        type_info = str(type(choices[keys[ioff]])).split("'")[1]
        print_str = f"({type_info}) "

        if self.opts["print_list_numbers"]:
          if type(keys[choice]) == int:
            print_str += "0" if int(keys[choice]) < 10 else ""
          print_str += f"{keys[ioff]} - "

        column_rest = x - (len(print_str) +5) # 5 because boarders on both sides + len("...")
        print_str += str(choices[keys[ioff]])[:column_rest]
        print_str += "..." if len(str(choices[keys[ioff]])) >= column_rest else ""
        c.main_w.addstr(i+1,1,print_str, c.curses.A_REVERSE if choice == ioff else c.curses.A_NORMAL)
        if i == y-3: break

      if (self.mode == "search" or user_line != "") and self.mode != "command":
        c.main_w.addstr(y-1,1,f"({self.len_resdir})/{user_line} >",c.curses.A_BOLD if self.mode == "search" else c.curses.A_NORMAL)
      elif self.mode == "command": 
        c.main_w.addstr(y-1,1,f"($):{user_line} >",c.curses.A_BOLD)

      c.main_w.refresh()
      info["yx_pop_w"] = (y,x)
      y,x = c.info_w.getmaxyx()
      info["yx_info_w"] = (y,x)

      # draw info_w (info window)
      try:
        user_key_ord = ord(user_key)
      except TypeError as e:
        user_key_ord = "-"
        self.log(f"{e=}","user key is special char")

      def str_splitter(str_, n): 
        return [str_[i:i+n] for i in range(0, len(str_), n)]
       
      info_str  = f"{choice}/{len(choices)-1}|in: {user_key}/{user_key_ord}"
      info_str += f"|r: {self.n_rec}|sm: {self.mode}"
      line_str = ""
      try:
        key_str = f"<{keys[choice]}>"
      except IndexError:
        key_str = "<->"
        self.log("{e=}","info_w key_str error")
      for i in range(x-2):  line_str += "-"
      
      if len(preview) == 0:
        preview_strs = str_splitter(str(choices[keys[choice]]).replace('\n', ' '),x-2)
      else:
        preview_strs = []
        try:
          for i in str(preview[choice]).split('\n'):
            if len(i) > x-2:
              preview_strs += str_splitter(i,x-2)
            else:
              preview_strs.append(i)
        except IndexError:
          preview_strs = str_splitter(str(choices[keys[choice]]).replace('\n', ' '),x-2)

      with c.render(c.info_w) as scr:
        c.info_w.box()
        c.info_w.addstr(1,1,info_str)
        c.info_w.addstr(1,x//2,"| h,j,k,l -> move, q -> return")
        c.info_w.addstr(2,1,line_str)
        c.info_w.addstr(0,1,key_str)
        for i in range(len(preview_strs)):
          c.info_w.addstr(3+i,1,preview_strs[i])
          if i == y-5: break

      c.info_w.refresh()
      # get user_key
      if user_key != None and skip_input_once == False:
        user_key = c.stdscr.getkey()
      else:
        skip_input_once = False
      info["key"] = user_key

      can_scroll_up   = lambda:choice > 0
      can_scroll_down = lambda:choice < len(choices)-1 
      def scroll_up(c=choice,o=offset):
          if (c-o) == 0: 
            o -= 1
          c -= 1
          return c,o
      def scroll_down(c=choice,o=offset,sc=screen_fit):
          if (c-o) == sc:
            o += 1
          c += 1
          return c,o

      if self.mode == "normal":
        if   user_key in ['k',"KEY_UP"] and can_scroll_up():
          choice, offset = scroll_up()
        elif user_key in ['j', "KEY_DOWN"] and can_scroll_down():
          choice, offset = scroll_down()
        elif user_key == 'K':
          if (choice-(screen_fit*2)) > 0:
            choice -= screen_fit
            offset -= screen_fit
          else:
            choice = offset = 0
        elif user_key == 'J':
          if (choice+(screen_fit*2)) < len(choices)-1:
            choice += screen_fit
            offset += screen_fit
          else:
            choice = len(choices)-1
            offset = choice - screen_fit
        elif user_key == '?': ranger_help(info, (len(info)*2,c.max_x-8,4,4))
        elif user_key == '/': self.mode = "search"
        elif user_key == ':': self.mode = "command"
        elif user_key == None: user_key = 'k' ; continue
        elif user_key in self.break_list: break

      elif self.mode == "search":
        import re
        user_key, user_line = handle_line_input(user_key, user_line)

        if user_key in ['\n', "KEY_RIGHT", "KEY_LEFT"]:
          if self.opts["endless_search_mode"]:
            user_line = ""
            user_key = ' '
            skip_input_once = True
            break
          else:
            user_line = user_line[:-1]
            self.mode = "normal"
        elif user_key == "KEY_UP" and can_scroll_up():
          choice, offset = scroll_up()
        elif user_key == "KEY_DOWN" and can_scroll_down():
          choice, offset = scroll_down()
        else: #if not enter -> perform re.search
          res_dir = {}
          choices = choices_

          if type(choices) == list:
            choices = {i : choices[i] for i in range(len(choices))}
          for k in choices:
            search = ""
            search = str(k) + str(choices[k])
            try:
              if re.search(user_line,search) != None:
                res_dir[k] = choices[k]
            except re.error as e:
              self.log(f"\nre.error={e}\n{k=}\n{search}")
              res_dir = choices 
              break
          self.len_resdir = len(res_dir)
          if self.len_resdir >= 1:
            choices = res_dir
      elif self.mode == "command":
        user_key, user_line = handle_line_input(user_key, user_line)
        if user_key == '\n': #enter
          self.mode = "normal"
          info["cmd"] = user_line[:-1]
          break

    self.log(f"{choice=}\n{choices[keys[choice]]=}","get_choice return ->")
    return choices[keys[choice]], info

nav = Nav().navigate

from os import popen
def prep_data(cwd):
  cmd  = f"ls -hals --group-directories-first {cwd}"
  cmd += "|sed 's/ [0-9]*,//;s/^total.*$//' |  column -o \"|\" -t"
  cmd = cmd.replace('\n', ' ')
  pop = popen(cmd).read().split("\n")
  data = [i.split("|") for i in pop]
  return data

class CNav(Nav):
   
  def file_manager_hnd(self, iterable):
    self.log("cnav started!","-----------------------------")
    self.break_list.append('~')
    cwd = popen("pwd").read()[:-1]
    # cwd = "/"
    while True:
      self.opts["main_w_title"] = f"<cnav@{cwd}"
      self.log(f"{cwd=}","prep data")
      dir_content = []
      for i in prep_data(cwd):
        try:
          i = " | ".join([i[1],i[9]])
          dir_content.append(i)
        except IndexError:
          break
      choice, info = self.get_choice(dir_content,["qb\nc\ndef \nWORKING!",])
      choice  = choice.split("|")
      choice[-1] = choice[-1].replace(" ","")

      if info["key"] in ['h',"KEY_LEFT"] or choice[-1] == "..":
        self.n_rec -= 1
        cwd = cwd.split('/')
        cwd = '/'.join(cwd[:-1])
        continue
      elif choice[-1] != ".":
        cwd += ("/" + choice[-1].replace(" ",""))
        self.n_rec += 1

      self.log(f"{choice[0]=}", "determing type")
      if choice[0][0] == 'd':
        self.log("","is dir")
      elif choice[0][0] == '-':
        info["cmd"] = "du"
        self.log("","is file")
      else:
        self.log("","is smt. else")


      if "cmd" in info:
        from os import system
        cmd = ""
        if info["cmd"] == "cd":
          self.log(f"{info['cmd']=}","got cmd")
          cmd = f"cd {cwd} && bash"
        elif info["cmd"] == "du":
          choice1, info1 = self.get_choice(["nvim","disk usage","tail"])
          if choice1 == "nvim": 
            cmd = f"nvim {cwd}"
        else:
          cwd = cwd.split('/')
          cwd = '/'.join(cwd[:-1])

        if cmd != "":
          self.c.__exit__(None,None,None)
          system(cmd)
          self.c.__enter__()
            

      elif info["key"] == '~':
        cwd = popen("echo $HOME").read()[:-1]

      if (t := type(choice)) != dict and t != list or info["key"] == 'q':
        return choice

nav = CNav()
nav.hnd_pointer = nav.file_manager_hnd
nav.opts["print_list_numbers"] = False

data = prep_data(None)
print(nav.navigate(data))


# pseudo code "cnav":
# | 1 | d | get cwd                    |
# | 2 | d | get selection from nav     |
# | 3 |   | if selection == '../' or h | cwd -- |
# | 4 |   | if selection is dir        |
# | 5 |   | else cwd = cwd + selection |
# | 6 |   | if selection is file       |
# | 7 |   | preview file               |

'''
help(nav.c.stdscr.getkey)
with (c := nut.Curses()):
  w = c.popup(title_str="tst", coords=(c.max_y-2,c.max_x-4,1,2))
  while True:
    in_ = w.getkey()
    if in_ == '\n': break
    w.clear()
    w.box()
    w.addstr(1,1,in_)
    w.refresh()
'''
