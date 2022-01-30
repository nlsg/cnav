cnav 
====
##a simple but powerful navigator implemented with curses
<!-- ![](https://i.imgur.com/SPwZKJN.mp4) -->

<!-- ![](https://imgur.com/a/LeMHIjp.gif) -->
`cat example.json | cnav.py`
![](https://i.imgur.com/6idnPhj.gif)

cnav can be used to interactively choose an item, or seek through
iterable objects like lists dicts, and mixtures of it.
if the object to iterate is a list, it gets converted to a dict, which keys are just numbers
it is not ment to be implemented in a real project, more as a helper tool
when scraping html content for example.

##usage

##features
- provide a regex to narrow down the selection
- select and return multiple objects
- send code to the REPL and see the output 

- standalone cnav is capable of reading stdin, but since curses messes with stdout,
it cannot	fully be used in a pipe chain.
- send a command which is handled by the recursion-hndl function
- all functionallity of cnav is implemented in just one class,

## customisation
- all keybindings can easily be overwritten, an action can be mapped to multiple keybindings

##dependencies
- dependent on nls_util's curses wrapper, this class will later be implemented into this project

##drawbacks and flaws
at this point cnav uses verious systemcalls, which means its UNIX only,
this is going to be fixed soon.

##todos
- the get_key_history function probably throws an error, if the navigate method has not been called before
- sort option for choices
-! option to toggle endless search mode
- optimised window redrawing(interessting framework https://github.com/jwlodek/py_cui)
