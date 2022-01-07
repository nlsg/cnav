#!/usr/bin/bash
PATH=$PATH:~/py/cnav
  ps -e -o pid,vsz=MEMORY,comm,args \
    | awk '{print $2","$1",\""$3"\",\""$4"\"]"}' \
    | column -s "," -o "," -t \
    | sort -rg \
    | sed '/^0/d' \
    | awk '{print "["$0}' \
    | cnav.py 
cat tmp | cnav.py

#!/usr/bin/python
# from os import popen 
# get_processes = " | ".join([
#    "ps -e -o pid,vsz=MEMORY -o comm "
#   ,"awk '{print $2\",\"$1\",\\\"\"$3\"\\\"]\"}' "
#   ,"column -s ',' -o ',' -t "
#   ,"sort -rg "
#   ,"sed '/^0/d' "
#   ,"awk '{print \"[\"$0}' "
#     ])
# pop_data = popen(get_processes).read()
# print(pop_data)

