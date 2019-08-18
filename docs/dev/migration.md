## Migration

### General

 - Often `push` is used to add an element to an array in Stylus; in Stilus an `append` needs to be used.

### Stack

 - A `scope` has `commons`, not `globals`

### Nodes

 - All `node` types are set via the `node_name` attribute.
 - The `value` attribute of a `node` is used to denote its value, while in Stylus JavaScript implementation `val` is used.

### Cases

The cases in Stylus were checked after trimming (stripping in Python) the generated css.
In Stilus that is not the case.  The styl and css files are now compared as they are.
