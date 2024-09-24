from matplotlib import pyplot as plt
from trepro.matplotlib import load_saved_figure, patch_savefig

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
patch_savefig()
plt.savefig("test.png")

# --- load saved figure ---

fig, metadata = load_saved_figure("test.png")
print(metadata)
