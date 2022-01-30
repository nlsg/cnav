#!/usr/bin/python3
from sys import path; path.insert(1, '/home/nls/py/pytools');
import nls_util as nut
notify = nut.notify
class Nav():
  def __init__(self):
    # ui/ux related
    self.c = nut.Curses()
    self.opts = {
       "print_list_numbers":True
      ,"print_type":True
      ,"endless_search_mode":True
      ,"lock_regex":None # lock regex not working yet!
      ,"horizontal_split":False
      ,"main_w_title":"<cnav>"
      ,"hilight_attr":self.c.curses.A_REVERSE
      }
    self.keybinding_info = {
       "j, k"    :" -> Down, Up"
      ,"J, K"    :" -> PgDn, PgUp"
      ,"q"       :" -> quit and return selected item"
      ,"g"       :" -> go to top"
      ,"G"       :" -> go to bottom"
      ,"<C-t>"   :" -> toggle endless_search_mode"
      }
    self.n_rec = 1
    self.debug_mode = False
    self.visual_markpoint = 0
    self.break_list = ['q', 'h', 'l', '\n',"KEY_LEFT","KEY_RIGHT"]
    self.hnd_pointer = self.recursion_hndl
    self.logfile = "cnav.log"
    self.mode = "normal"

  def log(self, log_data="", title=""):
    '''this method has nothing to do with cnav functionality!
    since debugging curses applications is a pain, i tend to debug them 
    with a file and or system notifications'''
    if self.debug_mode == True:
      import time as t
      log_str = t.strftime("%m-%d %H:%M:%S") + f" - {title} >\n"
      log_str += log_data.replace("\n", "\n  ") + "\n\n"
      with (f := open(f"{self.logfile}", "a")):
        f.write(log_str)
      notify(f"log", "log written!")

  def get_key_history(self):
    '''this method is useful to get the history of dict-keys after the navigate method gets called'''
    hist = ""
    for i in self.key_history:
      try:
        i = int(i)
      except ValueError:
        i = "\"" + i + "\""
      hist += f"[{i}]"
    return hist

  def navigate(self, iterable):
    '''this method is the hart and main entry point of cnav,
    it initalies the curses object 
    and wraps around recursion-hndl-function'''
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

    self.history = []
    self.key_history = []
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
    '''this is the default recursion-hndl, if you overwrite this method,
    make sure it calls the perform_navigation function at least once
    this function is ment to give a simple interface to handle custom key-events,
    commands and recursive calling of the perform_navigation method'''
    self.history.append(iterable)
    while True:
      self.choice, self.info = self.perform_navigation(self.history[-1])
      if self.info["key"] == 'h' and len(self.history) > 1:
        self.history.pop()
        self.n_rec -= 1
        continue
      else:
        if len(self.choice) > 1:
          return self.choice
        self.history.append(*self.choice)
        self.n_rec += 1
      if self.info["sr"][0] != self.info["sr"][1] and self.info["key"] == "q":
        return self.history[-1]
      if (t := type(self.choice[0])) != dict and t != list or self.info["key"] == 'q':
        return self.history[-1]

  def perform_navigation(self, choices, preview:list=[]):
    '''this method contains all functionality of cnav'''
    self.choices = choices
    c = self.c

    def str_splitter(str_, n): 
      return [str_[i:i+n] for i in range(0, len(str_), n)]
       
    def ranger_help(help_dict, coords):
      help_w = c.popup("<help>", coords)
      c.render_win(help_w,[f"{k}\t{help_dict[k]}" for k in help_dict])
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
                                
    self.choice = 0
    choices_ = self.choices
    self.len_resdir = len(self.choices)-1
    self.info = {}
    self.info.update(self.keybinding_info)
    self.info.update(self.opts)
    self.info["recursion_counter"] = self.n_rec
    self.offset = 0
    skip_input_once = False
    self.user_key = None 
    # lock_regex is either None or holds the user_line value of the last iteration
    if self.opts["lock_regex"] != None:
      self.user_line = self.opts["lock_regex"]
    else:
      self.user_line = ""

    def construct_main_w():
      selected_range = [self.choice,self.choice]
      if self.mode == "visual":
        if self.choice <= self.visual_markpoint:
          selected_range = [self.choice, self.visual_markpoint]
        else:
          selected_range = [self.visual_markpoint, self.choice]
      self.info["sr"] = selected_range
      main_strs = [] # contains str or (str,attr) to be drawn for addstr function

      if self.mode == "normal":
        main_strs.append([y-1,1,f"({self.len_resdir})"])
      if (self.mode == "search" or self.user_line != "") and self.mode != "command":
        main_strs.append([y-1,1,f"({self.len_resdir})/{self.user_line} >",c.curses.A_BOLD if self.mode == "search" else c.curses.A_NORMAL])
      elif self.mode == "command": 
        main_strs.append([y-1,1,f"($):{self.user_line} >",c.curses.A_BOLD])
      if self.mode == "repl": 
        main_strs.append([y-1,1,f"(>>>):{self.user_line} >",c.curses.A_BOLD])
      if self.mode == "visual": 
        main_strs.append([y-1,1,f"({selected_range[0]}:{selected_range[1]} /{self.len_resdir})",c.curses.A_BOLD])
      for i in range(len(self.choices)):
        ioff = i + self.offset
        print_str = ""
        if self.opts["print_type"]:
          type_info = str(type(self.choices[keys[ioff]])).split("'")[1]
          print_str = f"({type_info}) "
        if self.opts["print_list_numbers"]:
          if type(keys[self.choice]) == int:
            print_str += "0" if int(keys[i]) < 10 else ""
          print_str += f"{keys[ioff]} - "
        print_str += str(self.choices[keys[ioff]]).rstrip()
        if len(print_str) > x-2:
          print_str = print_str[:x-5] + "..."
        # if self.choice == ioff:
        if selected_range[0] <= ioff <= selected_range[1]:
          main_strs.append([print_str, self.opts["hilight_attr"]])
        else:
          main_strs.append(print_str)
        if i == y-3: break
      return main_strs
    
    def construct_info_w():
      try:
        user_key_ord = ord(self.user_key)
      except TypeError as e:
        user_key_ord = "-"
        self.log(f"{e=}\n{self.user_key=}","user key is special char")
      info_str  = f"{self.choice}/{len(self.choices)-1}|in: {self.user_key}/{user_key_ord}"
      info_str += f"|r: {self.n_rec}|sm: {self.mode}|c: {self.choice}, o: {self.offset}"
      line_str = ""
      info_str = str_splitter(info_str,x-2)[0]
      try:
        key_str = f"<{keys[self.choice]}>"
      except IndexError:
        key_str = "<->"
        self.log("{e=}","info_w key_str error")
      for i in range(x-2):  line_str += "-"
      
      if len(preview) == 0:
        preview_strs = str_splitter(str(self.choices[keys[self.choice]]).replace('\n', ' '),x-2)
      else:
        preview_strs = []
        try:
          for i in str(preview[self.choice]).split('\n'):
            if len(i) > x-2:
              preview_strs += str_splitter(i,x-2)
            else:
              preview_strs.append(i)
        except IndexError:
          preview_strs = str_splitter(str(self.choices[keys[self.choice]]).replace('\n', ' '),x-2)
      return [key_str,info_str,line_str, *preview_strs]

    can_scroll_up   = lambda:self.choice > 0
    can_scroll_down = lambda:self.choice < len(self.choices)-1 
    def scroll_up():
      if can_scroll_up():
        if (self.choice-self.offset) == 0: self.offset -= 1
        self.choice -= 1
    def scroll_down(sc=None):
      if can_scroll_down():
        if (self.choice-self.offset) == sc: self.offset += 1
        self.choice += 1
    def scroll_page_up(sc=None):
      if (self.choice-(sc*2)) > 0:
        self.choice -= sc
        self.offset -= sc
      else:
        self.choice = self.offset = 0
    def scroll_page_down(sc=None):
      if (self.choice+(sc*2)) < len(self.choices)-1:
        self.choice += sc
        self.offset += sc
      else:
        self.choice = len(self.choices)-1
        self.offset = self.choice - sc


    def filter_selection(choices_):
      import re
      res_dir = {}
      self.choices = choices_
      if type(self.choices) == list:
        self.choices = {i : self.choices[i] for i in range(len(self.choices))}
      for k in self.choices:
        search = str(k) + str(self.choices[k])
        try:
          if re.search(self.user_line,search) != None:
            res_dir[k] = self.choices[k]
        except re.error as e:
          self.log(f"\nre.error={e}\n{k=}\n{search}")
          res_dir = self.choices 
          break
      self.len_resdir = len(res_dir)
      if self.len_resdir >= 1:
        self.choices = res_dir
      return self.choices

    # handle mode independent keys
    def handle_independent_keys():
      """
      20 -> Ctrl+T
      16 -> Ctrl+P
      14 -> Ctrl+N
      """
      try:
        key_ord = ord(self.user_key)
      except TypeError:
        return False
      if key_ord == 20:
        self.opts["endless_search_mode"] = not self.opts["endless_search_mode"]
      elif key_ord == 16:
        scroll_up()
      elif key_ord == 14:
        if can_scroll_down(screen_fit):
          scroll_down(screen_fit)
      else: return False
      return True

    def handle_normal_keys():
      if self.mode != "normal":
        return False
      if   self.user_key in ['k',"KEY_UP"]:
        scroll_up()
      elif self.user_key in ['j', "KEY_DOWN"]:
          scroll_down(screen_fit)
      elif self.user_key in ['K', "KEY_PPAGE"]:
        scroll_page_up(screen_fit)
      elif self.user_key in ['J', "KEY_NPAGE"]:
        scroll_page_down(screen_fit)
      elif self.user_key == 'g': self.choice = 0; self.offset = 0
      elif self.user_key == 'G': self.choice = len(self.choices)-1; self.offset = self.choice-screen_fit
      elif self.user_key == '?': ranger_help(self.info, (len(self.info)*2,c.max_x-8,4,4))
      elif self.user_key == '/': self.mode = "search"
      elif self.user_key == ':': self.mode = "command"
      elif self.user_key == '>': self.mode = "repl"
      elif self.user_key == 'v': self.mode = "visual"; self.visual_markpoint = self.choice
      elif self.user_key in self.break_list: return "break"
      else: return False
      return True

    def handle_search_keys():
      if self.mode != "search":
        return False
      self.user_key, self.user_line = handle_line_input(self.user_key, self.user_line)
      if self.opts["lock_regex"] != None:
        self.opts["lock_regex"] = self.user_line
      if self.user_key in ['\n', "KEY_RIGHT", "KEY_LEFT"]:
        if self.opts["endless_search_mode"]:
          self.user_line = ""
          self.user_key = ' '
          skip_input_once = True
          return "break"
        else:
          self.user_line = self.user_line[:-1]
          self.mode = "normal"
      elif self.user_key == "KEY_UP":
        scroll_up()
      elif self.user_key == "KEY_DOWN":
        scroll_down(screen_fit)
      else: #if not enter -> perform re.search
        self.choices = filter_selection(choices_)
      return True

    def handle_command_keys():
      if self.mode != "command":
        return False
      self.user_key, self.user_line = handle_line_input(self.user_key, self.user_line)
      if self.user_key == '\n': #enter

        self.mode = "normal"
        self.info["cmd"] = self.user_line[:-1]
        return "break"

    def handle_visual_keys():
      if self.mode != "visual":
        return False
      if self.user_key in ["^[","\n","l","h","v","q"]:
        self.mode = "normal"
        if self.user_key in ["\n","q"]:
          return "break"
      elif self.user_key in["KEY_UP", "k"]:
        scroll_up()
      elif self.user_key in ["KEY_DOWN", "j"]:
        scroll_down(screen_fit)
      elif self.user_key == 'K':
        scroll_page_up(screen_fit)
      elif self.user_key == 'J':
        scroll_page_down(screen_fit)
      elif self.user_key == '?': ranger_help(self.info, (len(self.info)*2,c.max_x-8,4,4))
      else: return False
      return True

    def handle_repl_keys():
      if self.mode != "repl":
        return False
      self.user_key, self.user_line = handle_line_input(self.user_key, self.user_line)
      if self.user_key == '\n': #enter
        self.mode = "normal"
        try:
          evaled = eval(self.user_line[:-1])
          choice1, info1 = self.perform_navigation(str(evaled).split("\n"))
        except Exception as e:
          self.debug_mode = True
          self.log(f"{e=}\n{self.user_line=}","raised exception while eval")
          from sys import exit; exit(1)
        return True
      return True

    handlers = [
        handle_independent_keys,
        handle_normal_keys,
        handle_search_keys,
        handle_command_keys,
        handle_visual_keys,
        handle_repl_keys,
        ]
    while True:
      if type(self.choices) == list: 
        keys = [i  for i in range(len(self.choices))]
      else:
        keys = list(self.choices.keys())

      if self.choice > len(self.choices)-1:
        self.choice = self.offset = 0

      y,x = c.main_w.getmaxyx()
      screen_fit = y-3
      c.render_win(c.main_w, construct_main_w(), self.info["main_w_title"])
      y,x = c.info_w.getmaxyx()
      c.render_win(c.info_w, construct_info_w())

      if self.user_key != None and skip_input_once == False:
        try:
          self.user_key = c.stdscr.getkey()
        except Exception as e:
          self.log(f"{e=}", "get key error")
      else:
        skip_input_once = False
      self.info["key"] = self.user_key

      if self.user_key == None:
        self.user_key = 'k'
        continue
      for hnd in handlers:
        ctrl_flow = hnd()
        if ctrl_flow != False:
          break
      if ctrl_flow == "break":
        break
      elif ctrl_flow == True:
        continue
      
    if self.user_key not in ["h","KEYLEFT"]:
      self.key_history.append(keys[self.choice])

    # return a selection
    if self.info["sr"][0] != self.info["sr"][1]:
      self.info["sr"][1] += 1
      return [self.choices[keys[i]] for i in range(*self.info["sr"])], self.info

    # return an object
    return [self.choices[keys[self.choice]],], self.info

def eval_input(in_):
  '''try to evaluete lines in input
  and append them to res
  an alernative to this is json.dump()'''
  import json
  res = []
  try:
    res = json.loads("".join(in_))
  except (TypeError, json.decoder.JSONDecodeError):
    from ast import literal_eval
    for ln in in_:
      try:
        res.append(literal_eval(ln))
      except (TypeError, ValueError, SyntaxError) as e:
        res.append(str(ln))
  return res

def stdin_to_list():
  '''trys to evalute stdin
  (works if it is a nested iterable object e.g. [[23,[23,4,33]],'qbc',{'12':13,},2,34])
  otherwise converts it to string'''
  lines = []
  with open(0) as stdin:
    if not (is_tty := stdin.isatty()):
      lines = stdin.readlines()
    else:
      lines = None
  if lines == None:
    return ["no stdin",]
  return eval_input(lines)

def reattach_tty():
  '''reatach tty after reading stdin
  return value has to be taken, though it is not used'''
  from os import dup2
  tty=open("/dev/tty")
  dup2(tty.fileno(), 0)
  return tty

def parse_args():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument("-o", "--outfile", help="write output to a file")
  parser.add_argument("-p", "--pipe", action="store_true", help="piping workaround, writes to /tmp/cnav (e.g. cat x | cnav.py -p ; cat /tmp/cnav | grep ...)")
  parser.add_argument("-r", "--readable", action="store_true", help="puts newlines after comas(true by default, -r to disable)")
  parser.add_argument("-j", "--json-format", default = "{[(),", help="put \\n after given chars")
  parser.add_argument("-f", "--format", help="dont use json output forma, TODO!")
  return vars(parser.parse_args())

def check_args(args=parse_args()):
  opts = {}
  opts.update(args)
  opts["outfile"] = "/dev/stdout"
  if args["outfile"] != None:
    opts[file] = args["outfile"]
  if args["pipe"] == True:
    opts["outfile"] = "/tmp/cnav"
  return opts

if __name__ == "__main__":
  opts = check_args()
  obj = stdin_to_list()
  tty = reattach_tty()
  nav = Nav()
  nav.opts["endless_search_mode"] = True
  res = nav.navigate(obj)
  if opts["json_format"] != "":
    out = res
    for j_ in str(opts["json_format"]):
      out = str(out).replace(f"{j_}",f"{j_}\n")
  if opts["readable"]:
    out = str(res).replace(",","\n")
    for ch in ["{","}","[","]","(",")","\"","'"]:
      out = str(out).replace(ch,"")
  with open(opts["outfile"],"w") as f:
    f.write(out)
    f.write("\n")

      
