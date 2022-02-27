#!/usr/bin/python
from os import popen

def adb(cmd):
  return popen(f"adb shell {cmd}").read()

def adb_rm(pkg):
  return adb(f"pm uninstall -k --user 0 {pkg}")

def get_pkgs(search):
  pkgs = []
  for pk in adb(f"pm list packages | grep -E '{search}'").split("\n"):
    try:
      pkg = pk.split("package:")[1]
      pkgs.append(pkg)
    except IndexError:
      pass
  return pkgs

def rm_pkgs(search):
  for pkg in get_pkgs(search):
    adb_rm(pkg)

def search_pkgs(search):
  print(f"searching for '{search}' gave folowing results:")
  res = get_pkgs(search)
  for r in res:
    print(r)
  print(f"amount of pkgs: {len(res)}")

def rm_and_check(search):
  search_pkgs(search)
  if (in_ := input("remove [y/N]:\n>")) == "y" or in_ == "Y":
    rm_pkgs(search)
    print("removed!")
  else:
    print("deleting aborted!")
  search_pkgs(search)

# rm_and_check("google")

def choose_pkgs(search):
  from sys import path; path.insert(1, '/home/nls/py/cnav')
  from cnav import Nav
  nav = Nav()
  nav.opts["endless_search_mode"] = False
  nav.opts["horizontal_split"] = True
  res = nav.navigate(get_pkgs(search))
  from sys import path; path.insert(1, '/home/nls/py/pytools'); import nls_util as nut
  nut.notify(f"{type(res)}")
  return res[0]

def interactive_rm():
  while True:
    pkgs = choose_pkgs(input("search term: "))
    for pkg in pkgs:
      print(f" - {pkg}")
    if (in_ := input("remve these packages [y/N]: ")) == "y" or in_ == "Y":
      print("removed!")
      for pkg in pkgs:
        adb_rm(pkg)
    else:
      print("aborted!")
if __name__ == "__main__":
  interactive_rm()
