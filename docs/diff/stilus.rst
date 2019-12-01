
The stilus binary
=================

Stilus is currently aiming for Stylus version 0.54.5.

Implemented
-----------

Usage: stilus [OPTIONS] [INPUT] [OUTPUT]

Just like in Stilus, the stdin and stdout streams can be used.

These options now work:

======================== ===========================================
option                   description
======================== ===========================================
--out -o <dir>           Output to <dir> when passing files
--watch -w               Watch file(s) for changes and re-compile
--compress -c            Compress CSS output
--help, -h               Show help
--verbose -v             More verbose output
--watch -w               Watch file(s) and recompile when changed
--print, -p              Print css even when streaming to output
--prefix, -P [prefix]    Prefix all css classes by <prefix>
--include, -I <path>     Add <path> to the lookup paths list
--hoist-atrules          Move @import and @charset to the top
--version, -V            Show the version
======================== ===========================================


Todo
----

Stylus also supports these options:

======================== ===========================================
option                   description
======================== ===========================================
-i, --interactive        Start interactive REPL
-u, --use <path>         Utilize the Stylus plugin at <path>
-U, --inline             Utilize image inlining via data URI support
-C, --css <src> [dest]   Convert CSS input to Stylus
-d, --compare            Display input along with output
-f, --firebug            Emits debug info
-l, --line-numbers       Emits comments
-m, --sourcemap          Generates a sourcemap in sourcemaps v3 format
--sourcemap-inline       Inlines sourcemap with full source text in base64 format
--sourcemap-root <url>   "sourceRoot" property of the generated sourcemap
--sourcemap-base <path>  Base <path> from which sourcemap and all sources are relative
--import <file>          Import stylus <file>
--include-css            Include regular CSS on @import
-D, --deps               Display dependencies of the compiled file
--disable-cache          Disable cachi
-r, --resolve-url        Resolve relative urls inside imports
--resolve-url-nocheck    Like --resolve-url but without file existence check
======================== ===========================================
