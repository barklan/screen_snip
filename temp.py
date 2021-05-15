import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns


class Blog:
    def __init__(self, filename, figsize=(6, 6), axis=True, palette="bright"):
        self.filename = filename
        self.figsize = figsize
        self.axis = axis

    def set_plot(self, figsize=(6, 6)):
        sns.set()
        sns.set_theme(style="white", palette="bright")
        COLOR = "grey"
        mpl.rcParams["text.color"] = COLOR
        mpl.rcParams["axes.labelcolor"] = COLOR
        mpl.rcParams["xtick.color"] = COLOR
        mpl.rcParams["ytick.color"] = COLOR
        plt.figure(figsize=self.figsize)
        sns.set_context("paper")

    def save_plot(self):
        if self.axis:
            plt.axis("on")
        else:
            plt.axis("off")
        plt.savefig(self.filename, format="svg", bbox_inches="tight", pad_inches=0.3, transparent=True)

    def __enter__(self):
        self.set_plot()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.save_plot()


x = np.arange(0, 10, 0.00001)
y = x * np.sin(2 * np.pi * x)
fmri = sns.load_dataset("fmri")

with Blog("fmri.svg", figsize=(7, 7), axis=True):
    sns.lineplot(x="timepoint", y="signal", hue="region", style="event", data=fmri)
