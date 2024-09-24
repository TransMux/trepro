<div align="center">
    <h1>Trepro</h1>
    <em>Reproduce everything...</em>
    &nbsp;&nbsp;&bull;&nbsp;&nbsp;
    <em><code>pip install trepro</code></em>
</div>

<p align="center">
    <a href="https://pypi.org/project/trepro/">
        <img alt="codecov" src="https://img.shields.io/pypi/pyversions/tyro" />
    </a>
</p>

<br />

What **Trepro** afford:

- Save and load matplotlib figures with metadata, so you can **recover the state of the figure whenever you want**.

- More coming soon...

## Using Trepro

### Install

```bash
pip install trepro
```

## ✨ Recover Figure with Metadata ✨

![alt text](docs/assets/cee7ed27cc2e9f698c16be907444e1b.png)

```diff
from matplotlib import pyplot as plt
+ from trepro.matplotlib import load_saved_figure, patch_savefig

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

+ patch_savefig() # patch savefig to save metadata

plt.savefig("test.png")

# --- load saved figure ---

+ fig, metadata = load_saved_figure("test.png")
+ print(metadata)
```
