cnav 
====
## a simple but powerful navigator implemented with curses

`cat example.json | cnav.py`

![](https://imgur.com/5KAiEZ9.gif)
![](https://i.imgur.com/6idnPhj.gif)

`cnav` can be used to interactively choose and return one or multiple items from a json file,
or seek through iterable objects like lists dicts, and mixtures of it.
If the object to iterate is a list, it gets converted to a dict, which keys are just numbers.
`cnav` is not meant to be implemented in a real project, more as a helper tool
when scraping html content for example.

`cnav` can be used standalone, in a Python REPL session or be inherited in a python project.
It can also be utilised in a shell script 

## features
- provide a regex to narrow down the selection (default binding '/')
- select and return multiple objects (default binding 'q')
- send code to the REPL and see the output (useless feature, will be removed)

- standalone `cnav` is capable of reading stdin, but since curses messes with stdout, 
it cannot fully be used in a pipe chain.
- send a command which is handled by the recursion_hndl function
- all functionality of `cnav` is implemented in just one class,

## default keybindings 
| keybinding      | action                                             |
|-----------------|----------------------------------------------------|
| j, k, up, down  | move up / down                                     |
| h, left         | go back                                            |
| l, right, enter | go further or return, if object is not iterable    |
| g, G            | move to first / last object                        |
| q               | return highlighted object(s)                       |
| v               | toggle to visual mode (to select multiple objects) |
| /               | toggle search mode (it uses regex from re module)  |
| Ctrl + t        | toggle endless_search_mode                         |
| Ctrl + c        | exit application                                   |
| #               | toggle print_line_numbers                          |

## modes 
| mode          | explanation             |
|---------------|-------------------------|
| visual mode   | select multiple objects |
| search mode*1 | filter objects          |

*1 there are two types of search modes endless and normal
if the endless search mode is active, you will stay in search mode after going further


## customisation
- all keybindings can easily be overwritten, an action can be mapped to multiple keybindings
- options are stored in a dict called opts (e.g. Cnav().opts["print_type"])
changing an option:
```
from cnav import Nav
nav = Nav()
nav.opts["endless_search_mode"] = False
```

| option              | default                            |
|---------------------|------------------------------------|
| print_list_numbers  | True                               |
| print_type          | True                               |
| endless_search_mode | True                               |
| lock_regex          | None # lock regex not working yet! |
| horizontal_split    | False                              |
| main_w_title        | "<cnav>"                           |
| hilight_attr        | self.c.curses.A_REVERSE            |


## dependencies
- curses 

## drawbacks and flaws
at this point cnav uses various system calls, which means its UNIX only,
this is going to be fixed soon.

## todos
- make if posssible to select multiple selections with spaces in between
- the get_key_history function probably throws an error, if the navigate method has not been called before
- sort option for choices
- optimised window redrawing(interessting framework https://github.com/jwlodek/py_cui)
- make it possible to iterate further when multiple objects are selected 
