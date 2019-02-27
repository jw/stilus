## History

### 0.5.0 

The first evaluate a.k.a. the `let's lever commit` release.

 - Created the evaluate class.
 - Parsed and evaluated the `index.styl`.
 - Ran some Stylus `cases` tests successfully.

Issues:
 
 - [x] Check `poetry`, `pylama` and `radon`: will not use it.
 - [x] Document the history, the todo's, the workflow
 - [x] Add contribution data: code of conduct, issue template, pull request template
 - [x] Finalize the compiler
 - [x] Create and complete the Evaluator (in progress... at 50%)
 - [x] Create and complete the Normalizer
 - [x] Compile `abc\n  color: red\n` successfully
 - [x] Fix the `type` problem
 - [x] Add logging to the project
 - [x] Add the same tests as in Stylus; two are green!
 - [x] Complete the parser
 - [x] Fix the `stack` problem; completed
 - [x] Fix the `val` problem; completed (almost all `val`s are `value`s now)
 - [x] Compile the complete `index.styl`
 - [x] Add column and lineno to tokens (lexer and parser and compiler)
 - [x] Fix the `space` problem
 - [x] Fix the `string` problem
 - [x] Pass a Stylus 'cases' test
 - [x] Evaluator: Fix the multiple imports problem.

### 0.4.0 

The first compile.

 - First compile of a very simple styl: `abc\n  color: red\n`.
 - Completed the parser for 90% and finalized the lexer.
 - Created a very basic compiler.
 - Added more nodes (70% complete) and added the stack.

### 0.3.0

CI and documentation.

 - Created CI via Travis; Added flake8.
 - Created Sphinx documentation.
 - Completed the lexer.

### 0.2.0

 - Added some extra nodes and updated the lexer.
 - Checked the `black` tool; do not like it.
 
### 0.1.0

 - Basic lexer and some pytested nodes.

### 0.0.1

Hello there!

 - Basic Python 3.6 setup, using pipenv and a basic setup.py.
 - Created a Stilus hello world.