## History

### 0.7.0

The Swedish release, a.k.a. `document, document, document!`

 - [x] Update the Stilus bin:
   - [x] create bin app
   - [x] add compression flag
 - [x] Pass 100 Stylus test cases.  At 161!  :-)
 - [x] Start spreading the word in pycon Sweden.
 - [x] Show diff between Stilus and Stylus.
   - [x] Test diff
   - [x] Bin diff
 - [x] Get to 85% coverage.  At 89%!

### 0.6.0

The first cases release, a.k.a. `committers, committers, committers!`

 - [x] Added all remaining nodes.
 - [x] Recreated the `.clone()` method for all nodes; the current one were far too slow; and very WRONG!
 - [x] Add 3.7 and 3.8 Python.
 - [x] Start using Sphinx and web documentation: https://stilus.readthedocs.io.
 - [x] Pass 50 Stylus test cases.  79/50 done, or 158%.
 - [x] Try to get coverage above 70%. Aim for 80%; 75% will be fine.  At 82%!
 - [x] Create all builtin functions. 62/62 done, or 100.00%.
 - [x] Fixed the big `visit_block()` and `mixin()` problem in the evaluator.

### 0.5.0 

The first evaluate a.k.a. the `let's never commit` release.

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