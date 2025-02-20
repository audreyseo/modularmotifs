DSL for Actions on Designs
=====================================

In order to easily remember which actions were taken and when, so that
they can be done/undone in the GUI, and designs can be saved as text
files that are simply...python programs.

The "grammar" for the DSL looks something like this:

```
action ::= add_motif(motif, x, y) | remove_motif(placed_motif)
```

...it's a very silly and dumb DSL.
