# modularmotifs

**This is a class project and a work in progress.**

Run with `python3 -m modularmotifs.main`

Colorwork knitting design tool that allows modular editing, placement, tiling, etc. of motifs.


# Dependencies
This project generally uses poetry to manage python dependencies.

You will also need to install a [platform-specific version of
`tk`](https://stackoverflow.com/questions/25905540/importerror-no-module-named-tkinter).


This will need to coincide with your python version.


# Running tests
The python test framework `pytest` is included in the dev dependencies
for poetry. As long as poetry is set up, you should be able to run

```bash
poetry run pytest
```

in the repo's root directory, and it will run the test.

Tests should be in `tests/`.
