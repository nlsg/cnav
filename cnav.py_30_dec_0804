#!/usr/bin/python3
from nls_util import notify
class Nav():
  def __init__(self):
    self.opts = {
        "print_list_numbers":True
        }
    self.keybinding_info = {
       "j, k":" -> Down, Up"
      ,"J, K":" -> PgDn, PgUp"
      ,"q"   :" -> quit and return selected item"
      }
    self.n_rec = 1
    self.hnd_pointer = self.recursion_hndl
    self.chars_to_escape = ['[',']','\\']
    self.title_str = "<cnav>"
    self.logfile = "cnav.log"

  def log_to_file(self, log_data="", title=""):
    with (f := open(f"{self.logfile}", "a")):
      import time as t
      log_str = t.strftime("%m-%d %H:%M:%S") + f" - {title} >\n"
      log_str += log_data.replace("\n", "\n  ") + "\n\n"
      f.write(log_str)
      notify(f"log", "log written!")

  def navigate(self, iterable):
    self.history = [iterable]
    t = type(iterable)
    if t == dict:
      return self.hnd_pointer(iterable)
    elif t == list:
      list_to_dict = {i : iterable[i] for i in range(len(iterable))}
      return self.hnd_pointer(list_to_dict)
    elif t == str or t == int or t == bool:
      print("can't iterate anymore")

  def recursion_hndl(self, iterable):
    self.history.append(iterable)
    while True:
      choice, info = self.userinput(self.history[len(self.history)-1])
      if info["key"] == 'h' and len(self.history) > 1:
        self.history.pop()
        self.n_rec -= 1
        continue
      else:
        self.history.append(choice)
        self.n_rec += 1
      if (t := type(choice)) != dict and t != list or info["key"] == 'q':
        return self.history[len(self.history)-1]

  def userinput(self, choices):
    input()
    from nls_util import Curses
    choice = 0
    choices_ = choices
    with (c := Curses()):

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

      self.len_resdir = len(choices)-1
      in_ = None 
      info = {}
      info.update(self.keybinding_info)
      info.update(self.opts)
      info["recursion_counter"] = self.n_rec
      offset = 0
      search_mode = False
      search_query = ""

      while True:
        keys = []
        if (choices_type := type(choices)) == list: 
          keys = [i  for i in range(len(choices))]
          choices_type = "list"
        else:
          keys = list(choices.keys())

        c.stdscr.clear()
        pop_w = c.popup(title_str=self.title_str, coords=((c.max_y-4)//2,c.max_x-4,2,2))
        info_w = c.popup(title_str="<info>",   coords=((c.max_y-4)//2,c.max_x-4,(c.max_y//2),2))
        y,x = pop_w.getmaxyx()
        screen_fit = y-3
        
        # draw info_w (main window)
        for i in range(len(choices)):
          ioff = i + offset
          try:
            type_info = str(type(choices[keys[ioff]])).split("'")[1]
          except IndexError as e :
            self.log_to_file(f"\n(98)IndexError={e}\n{i=}, {ioff=}\n{len(choices)=}, {len(keys)=}")
            type_info = "NA"

          print_str = f"({type_info}) "
          if self.opts["print_list_numbers"] == False:# if  type_info == "list":
            pass
          else:
            if type(keys[choice]) == int:
              print_str += "0" if int(keys[choice]) < 10 else ""
            print_str += f"{keys[ioff]} - "
          column_rest = x - (len(print_str) +5)
          print_str += f"{str(choices[keys[ioff]])[:column_rest]}"
          print_str += "..." if len(str(choices[keys[ioff]])) >= column_rest else ""
          info["print_str"] = len(print_str)
          pop_w.addstr(i+1,1,print_str, c.curses.A_REVERSE if choice == ioff else c.curses.A_NORMAL)
          if i == y-3: break

        if search_mode or search_query != "":
          try:
            pop_w.addstr(y-1,1,f"({self.len_resdir})/{search_query}>",c.curses.A_BOLD if search_mode else c.curses.A_NORMAL)
          except Error as e:
            self.log_to_file(f"{e=}","Error while drawing search mode")

        pop_w.refresh()
        info["yx_pop_w"] = (y,x)
        y,x = info_w.getmaxyx()
        info["yx_info_w"] = (y,x)

        # draw info_w (info window)
        try:
          info_str  = f"{choice}/{len(choices)-1}|in: {in_}/{ord(in_)}"
          info_str += f"|r: {self.n_rec}|sm: {search_mode}"
          info_w.addstr(1,1,info_str)

        except TypeError as e:
          self.log_to_file(f"{e}","draw info_w")
          pass
        info_w.addstr(1,x//2,"| h,j,k,l -> move, q -> return")
        for i in range(x-2):  info_w.addstr(2,1+i,"-")
        info_w.addstr(2,2,f"<{keys[choice]}>")

        def str_splitter(str_, n): return [str_[i:i+n] for i in range(0, len(str_), n)]
        preview_strs = str_splitter(str(choices[keys[choice]]).replace('\n', ' '),x-2)
        for i in range(len(preview_strs)):
          info_w.addstr(3+i,1,preview_strs[i])
          if i == y-5: break

        info_w.refresh()
        if in_ != None:
          in_ = pop_w.getkey()
        info["key"] = in_
        if search_mode == False:
          if   in_ == 'k' and choice > 0:
            if (choice-offset) == 0: 
              offset -= 1
            choice -= 1
          elif in_ == 'j'  and choice < len(choices)-1 :
            if (choice-offset) == screen_fit:
              offset += 1
            choice += 1
          elif in_ == 'K':
            if (choice-(screen_fit*2)) > 0:
              choice -= screen_fit
              offset -= screen_fit
            else:
              choice = offset = 0
          elif in_ == 'J':
            if (choice+(screen_fit*2)) < len(choices)-1:
              choice += screen_fit
              offset += screen_fit
            else:
              choice = len(choices)-1
              offset = choice - screen_fit
          elif in_ == '?': ranger_help(info, (len(info)*2,c.max_x-8,4,4))
          elif in_ == '/': search_mode = True
          elif in_ == None: in_ = 'k' ; continue
          elif in_ in ['q', 'h', 'l', '\n']: break

        else: #search_mode
          import re
          choice = offset = 0
          if ord(in_) == 127: #delete
            search_query = search_query[:-1]
            if len(search_query) == 0:
              search_mode = False
          elif ord(in_) == 27: #escape
            search_query = ""
            search_mode = False
          else:
            search_query += in_
          if in_ == '\n':
            search_query = search_query[:-1]
            in_ = '~'
            search_mode = False
          else:
            res_dir = {}
            choices = choices_

            if type(choices) == list:
              choices = {i : choices[i] for i in range(len(choices))}
            for k in choices:
              search = ""
              search = str(k) + str(choices[k])
              # self.log_to_file(f"{type(k)=}, {type(choices)=}", "k is probably a dict")
              try:
                if re.search(search_query,search) != None:
                  res_dir[k] = choices[k]
              except re.error as e:
                self.log_to_file(f"\nre.error={e}\n{k=}\n{search}")
                res_dir = choices 
                break
            self.len_resdir = len(res_dir)
            if self.len_resdir >= 1:
              choices = res_dir

          pop_w.clear()  
        info_w.clear()  
    return choices[keys[choice]], info

nav = Nav().navigate

from os import popen
def prep_data(cwd, just_files=True):
  Nav().log_to_file(f"{cwd}", "in prep")
  cmd  = f"ls -als --group-directories-first {cwd}"
  cmd += "| awk '{print $2\" | \"$7$8\"_\"$9\" | \"$10}'"
  # cmd += "| grep " 
  # cmd += "" if just_files else "-v "
  # cmd += "-E \"^-\""
  cmd = cmd.replace('\n', ' ')
  Nav().log_to_file(f"{cmd}", "pre popen")
  pop = popen(cmd).read().split("\n")
  data = [i.split("|") for i in pop]
  return data

class CNav(Nav):
  def file_manager_hnd(self, iterable):
    cwd = popen("pwd").read()[:-1]
    cwd = "/"
    Nav().log_to_file(f"{cwd}", "pre prep")
    self.history.append(prep_data(cwd))
    input("pre while True")
    while True:
      self.title_str = f"<cnav@{cwd}"
      last_data = self.history[len(self.history)-1]
      for i in range(len(last_data)-1):
        del last_data[i][1]
      # self.log_to_file(f"{len(last_data)=}")
      choice, info = self.userinput(last_data)

      if info["key"] == 'h' and len(self.history) > 1:
        self.history.pop()
        self.n_rec -= 1
        cwd = cwd.split('/')
        cwd = '/'.join(cwd[:-1])
        continue
      else:
        # try:
        #   if choice[0][0] == 'd':
        #     self.log_to_file(f"\ndetected choice=dir\n{len(choice)=}\n{choice=}")
        #   if choice[0][0] == '-':
        #     self.log_to_file(f"\ndetected choice=not dir\n{len(choice)=}\n{choice=}")
        # except IndexError as e:
        #   self.log_to_file(f"\n(249)IndexError={e}\n{len(choice)=}\n{choice=}", "error detecting file")

        cwd += ("/" + choice[len(choice)-1]).replace(" ","")
        self.history.append(prep_data(cwd))
        self.n_rec += 1
      if (t := type(choice)) != dict and t != list or info["key"] == 'q':
        return self.history[len(self.history)-1]

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


