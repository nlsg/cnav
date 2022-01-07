#!/usr/bin/python
import cnav
from os import system, popen

# this is basically a simple shell script, 
# (you could also pipe it over stdin)
script = " | ".join([
   "ps -e -o pid,vsz=MEMORY,comm,args "
  ,"awk '{print $2\",\"$1\",\\\"\"$3\"\\\",\\\"\"$4\"\\\"]\"}' "
  ,"column -s ',' -o ',' -t "
  ,"sort -rg "
  ,"sed '/^0/d' "
  ,"awk '{print \"[\"$0}' "
    ])

# evaluate script
obj = cnav.eval_input(popen(script).read().split("\n"))

# feed it into cnav
nav = cnav.Nav()
nav.opts["endless_search_mode"]  =  False
nav.opts["print_type"]           =  False
res = nav.navigate(obj)

# kill the returned processes
cmds = []
print("[RAM usage, pid, comm, args]")
for i in res:
  print(i)
  cmds.append(f"kill {i[1]}")
if input("kill these procs? [N/y]: ") == "y":
  for cmd in cmds:
    system(cmd)
  print("killed all")


