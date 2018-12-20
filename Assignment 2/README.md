# Assignment 2: Prefix Trees and Melodies
## Overview
This assignment has 2 parts: Create a sophisticated autocompleter data type, and then use it to do some real work. 
For details, see (https://www.teach.cs.toronto.edu/~csc148h/fall/assignments/a2/handout/a2.html)

## Features
- Created a simple prefix tree type, and a compressed prefix tree type. The latter runs significantly faster. 
- Use the prefix tree types, create an autocompleter function that can return all (or limited) matching autocompleting results. 
- Made it work for text autocompletion.
- Made it work for melody autocompletion. (See handout for details)
- Using memoization and other techniques, cut unnecessary recursions so it works for extremely large inputs. 

## Known issues
- The melody autocompleter does not work as intended. There's something wrong with the engine that I haven't figured out. Trying to fix it. 
