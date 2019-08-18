
Blocks
======

In Stylus (in JavaScript) blocks in arrays are processed via

.. code-block:: javascript

    for (block.index = 0; block.index < block.nodes.length; ++block.index) {
      block.nodes[block.index] = this.visit(block.nodes[block.index]);
    }

But when a mixin is *visited*, the block.index is set to 0 and the block
is not updated.

In Stilus (Python) such a system is not possible; but a mixin attribute is used instead.

Both systems are ugly.
