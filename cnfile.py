#!/usr/bin/python
import cnav

class CNav(cnav.Nav):
  def file_manager_hnd(self, iterable):
    self.log("cnav started!","-----------------------------")
    self.break_list.append('~')
    cwd = popen("pwd").read()[:-1]
    # cwd = "/"
    while True:
      self.opts["main_w_title"] = f"<cnav@{cwd}"
      self.log(f"{cwd=}","prep data")
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
            pop = popen(f"{prog} {cwd_}").read()
          except UnicodeDecodeError as e:
            self.log(f"{e=}","popen(head) decode error")
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
      self.log(f"{data[info['choice']]=}","data reconstruction")
      choice  = choice.split("|")
      choice[-1] = choice[-1].replace(" ","")

      if info["key"] in ['h',"KEY_LEFT"] or choice[-1] == "..":
        self.n_rec -= 1
        cwd = '/'.join(cwd.split('/')[:-1])
        if cwd == "": cwd = "/"
        continue
      elif choice[-1] != ".":
        cwd += ("/" + choice[-1].replace(" ",""))
        # cwd += ("/" + "".join(data[info["choice"]][9:]).split(" ")[-1])
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

from os import popen
def prep_data(cwd):
  cmd  = f"ls -hals --group-directories-first {cwd}"
  cmd += "|sed 's/ [0-9]*,//;s/^total.*$//' "
  cmd += "|  column -o \"|\" -t"
  cmd = cmd.replace('\n', ' ')
  pop = popen(cmd).read().split("\n")
  data = [i.split("|") for i in pop]
  return data

def fm_test():
  nav = CNav()
  nav.hnd_pointer = nav.file_manager_hnd
  nav.opts["print_list_numbers"] = False

  data = prep_data(None)
  print(nav.navigate(data))

if __name__ == "__main__":
  fm_test()

