#!/usr/bin/python
from sys import path; path.insert(1, '/home/nls/py/cnav')
import cnav

class CNav(cnav.Nav):
  def file_manager_hnd(self, iterable):
    self.break_list.append('~')
    self.break_list.append('s')
    cwd = popen("pwd").read()[:-1]
    while True:
      self.opts["main_w_title"] = f"<cnav@{cwd}"
      dir_content = []
      dir_info = []
      it = 0
      for i in (data := prep_data(cwd)):
        it += 1
        try:
          cwd_ = cwd + "/" + "".join(i[9:]).rstrip()
          if i[1][0] == 'd':
            prog = "ls -a"
          elif i[1][0] == '-':
            prog = "head -n 4"
          try:
            # pop = popen(f"{prog} {cwd_}").read()
            pass
          except UnicodeDecodeError as e:
            self.log(f"{e=}","popen(head) decode error")
          pop = ""
          dir_content.append(" | ".join([
            i[1]
            ,*i[9:]
            ]))
          dir_info.append("\n".join([
            i[1]
            ," ".join([i_.rstrip() for i_ in i[9:]]).strip()
            ," ".join(i[6:9])
            ,pop
            ]))
        except IndexError:
          break
      choice, info = self.get_choice(dir_content,dir_info)

      choice  = choice[0].split("|")
      choice[-1] = choice[-1].replace(" ","")
      
      next_dir = "" #dir wich gets added to cwd
      for i in range(len(choice)-1,-1,-1):
        next_dir = choice[i].replace(" ", "")
        if next_dir != "": break


      def go_dir_up(cwd):
        self.n_rec -= 1
        cwd = '/'.join(cwd.split('/')[:-1])
        if cwd == "": cwd = "/"
        return cwd

      # mutate cwd
      if info["key"] in ['h',"KEY_LEFT"] or next_dir == "..":
        cwd = go_dir_up(cwd)
        continue
      elif info["key"] == '~':
        cwd = popen("echo $HOME").read()[:-1]
        continue
      elif next_dir != ".":
        cwd += ("/" + next_dir.replace(" ",""))
        self.n_rec += 1

      from os import system

      if info["key"] == 's':
        with self.c.detach(): system(f"cd {cwd} && bash")

      # evalute cmd
      if "cmd" in info:
        if "{}" in info["cmd"]:
          cmd = info["cmd"].replace("{}",f"{cwd}")
        with self.c.detach(): pop = popen(cmd).read()
        choice1, info1 = self.get_choice(pop.split("\n"))
      else:
        if choice[0][0] == 'd':
          self.log("","is dir")
        elif choice[0][0] == '-':
          choice1, info1 = self.get_choice(["nvim - system","du - popen","cat - popen","tail- system"])
          if info1["key"] != 'q':
            choice1 = choice1[0].split("-")
            cmd = f"{choice1[0]} {cwd}"
            if "system" in choice1[1]:
              with self.c.detach(): system(cmd)
            if "popen" in choice1[1]:
              with self.c.detach(): pop = popen(cmd).read()
              choice, info = self.get_choice(pop.split("\n"))
          self.log("","is file")
          cwd = go_dir_up(cwd)
        
      cwd = cwd.replace("//","/")

      if (t := type(choice)) != dict and t != list or info["key"] == 'q':
        return choice

from os import popen
def prep_data(cwd):
  cmd  = f"ls -hals --group-directories-first {cwd}"
  cmd += "|sed 's/ [0-9]*,//;s/^total.*$//' "
  cmd += "|  column -o \"|\" -t"
  cmd  = cmd.replace('\n', ' ')
  pop  = popen(cmd).read().split("\n")
  data = [i.split("|") for i in pop]
  return data

if __name__ == "__main__":
  nav = CNav()
  nav.hnd_pointer = nav.file_manager_hnd
  nav.debug_mode = True
  nav.opts["print_list_numbers"] = False
  nav.opts["print_type"] = False

  data = prep_data(None)
  print(nav.navigate(data))




