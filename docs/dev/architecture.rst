Architecture
============

The Stilus compiler reads a Stylus source file an produces a ccs file.

Parser
------

The Lexer reads the source file and splits it into Tokens.  The Parser
uses these tokens to create an `abstract syntax tree <https://en.wikipedia.org/wiki/Abstract_syntax_tree>`_ of nodes.

Nodes
-----

Each node denotes a structure occurring in the Stylus language.  For example
the *media* node contains the ``@media`` atrule in css; or the *boolean* node
contains a ``True`` and ``False`` value; the *each* node contains the content
of a for loop.

All nodes are extensions of the parent Node class.

In the nodes directory you'll find the complete list of all nodes.

Builtin functions
-----------------

A set of builtin functions are available.  For example, the ``clone()`` and
``convert()`` builtins are available.   See the functions directory for a
complete list.  These builtin methods are plain Python methods.

Some method are *raw* methods; others are not.

The index.styl file
-------------------

The index.styl file is automatically imported and becomes part of the ast.
It contains an extra list of builtin functions, but they are styl functions.

The abstract syntax tree
------------------------

The abstract syntax tree has a root.  The first element is the index.styl
file.  The other elements are added by the Parser while it reads the source
file(s).

When the source file is read successfully (i.e. when no parsing errors are
raised), the visitors are called.

The visitor pattern
-------------------

`The visitors pattern <https://en.wikipedia.org/wiki/Visitor_pattern>`_ is
used to process each *Node* element.  There are currently three visitors,
and they are processed in this order:

 1. Evaluator
 2. Normalizer
 3. Compiler

The Evaluator
^^^^^^^^^^^^^

Evaluates the tree.  This is the major visitor.

The Normalizer
^^^^^^^^^^^^^^

This visitor implements the first stage of the dual-stage compiler, tasked
with stripping the *garbage* from the evaluated nodes, ditching null rules,
resolving ruleset selectors et caetera.  This step performs the logic
necessary to facilitate the ``@extend`` functionality, as these must be
resolved *before* buffering output.

The Compiler
^^^^^^^^^^^^

Compile to css, and return a string of CSS.


Changes between Stylus and Stilus
---------------------------------

This section is quite useless.

Nodes
^^^^^

*Node* is the root of all nodes.  All *node* types are set via the
``node_name`` attribute.  The ``value`` attribute of a *node* is used to
denote its value, while in Stylus JavaScript implementation ``val`` is
used.

Evaluator
^^^^^^^^^

globals vs commons: the Stylus ``globals`` in the ``Evaluator`` is called
``commons``.

global vs common: the Styls ``global`` in the ``Evaluator`` is called
``common``.
