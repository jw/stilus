
Stilus
======

Stilus is currently aiming for Stylus version 0.54.5.

Implemented
-----------

Usage: stilus [OPTIONS] INPUT [OUTPUT]

Currently an input file is required, which produces an output.

These options now work:

======================== ===========================================
option                   description
======================== ===========================================
--help, -h               Show help
--verbose -v             More verbose output
--print, -p              Print css even when streaming to output
--include, -I <path>     Add <path> to the lookup paths list
--version, -V            Show the version
======================== ===========================================


Todo
----

Currently an input file is required, which produces an output.
But Stylus gets the input as a stream and produces an output.

It also supports these options:

======================== ===========================================
option                   description
======================== ===========================================
-i, --interactive        Start interactive REPL
-u, --use <path>         Utilize the Stylus plugin at <path>
-U, --inline             Utilize image inlining via data URI support
-w, --watch              Watch file(s) for changes and re-compile
-o, --out <dir>          Output to <dir> when passing files
-C, --css <src> [dest]   Convert CSS input to Stylus
-c, --compress           Compress CSS output
-d, --compare            Display input along with output
-f, --firebug            Emits debug info
-l, --line-numbers       Emits comments
-m, --sourcemap          Generates a sourcemap in sourcemaps v3 format
--sourcemap-inline       Inlines sourcemap with full source text in base64 format
--sourcemap-root <url>   "sourceRoot" property of the generated sourcemap
--sourcemap-base <path>  Base <path> from which sourcemap and all sources are relative
-P, --prefix [prefix]    prefix all css classes
--import <file>          Import stylus <file>
--include-css            Include regular CSS on @import
-D, --deps               Display dependencies of the compiled file
--disable-cache          Disable cachi
--hoist-atrules          Move @import and @charset to the top
-r, --resolve-url        Resolve relative urls inside imports
--resolve-url-nocheck    Like --resolve-url but without file existence check
======================== ===========================================
