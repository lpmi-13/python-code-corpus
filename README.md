# extracting python code blocks

**(currently used as a data source for https://examplar-code.netlify.app as well as https://parsons-problems.netlify.app)**

So I wanted to grab a bunch of example python code from real github projects.

The current code grabs the top 100 starred python repos (shamelessly adapted from https://github.com/EvanLi/Github-Ranking), though depending on the eventual uses, it might be nice to either selectively limit or expand that.

## source

Currently, the `url_list.txt` file, line-separated, is what's being used as the source of the URLs to clone and interate through.

This list is generated from `grab_repos.py` as follows:

```
$ python grab_repos --language python
```

## create abstract syntax trees and pull out the code snippets

First, `walker.py` goes through all the `.py` files in each repo and converts them to ASTs, then it walks the nodes and pulls out the following:

- for loops
- while loops
- if conditionals
- list assignment
- list comprehension assignment
- dictionary assignment
- dictionary comprehension assignment
- set assignment
- set comprehension assignment
- function definitions
- async function definitions

...and skips a bunch since sometimes the assignment is split across muliple lines, making it difficult to determine which line in the original file it started on. There's probably a simple regex to look for whether the variable and first character in the assignment match a line in the file...but I couldn't be bothered to deal with that, since there are oodles of examples that come out, so I didn't necessarily feel like being exhaustive.

Anyway, all these examples are put into a mongo db instance, with each type of AST node as a separate collection.

**(NOTE: if you would like to remove the locally cloned github repos after processing, pass the `-D` flag)**

```
$ python walker.py --language python -D
```

## pull out the data into a big json file

`extract.py` writes out the first 25 items from the following to a json file:

- for loops
- if conditionals
- list assignment
- list comprehension assignment
- dictionaries
- dictionary assignment
- dictionary comprehension assignment
- functions

(just using the above to generate data for a web app to show what the examples
look like...will possibly create REST API or GraphQL API if I'm feelin funky later)
