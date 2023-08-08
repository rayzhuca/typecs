import random
import string
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from matplotlib.patches import Ellipse

from sklearn.cluster import KMeans

matplotlib.use('agg')

import numpy as np

def get_wpm(timetable): # [t, {key: 'a', correct: True/False}]
    cps = [0] * 30 # characters per second
    for [t, stamp] in timetable:
        if stamp["correct"]:
            cps[min(int(t), 29)] += 1
    wpm = [(60 * x) / 4.7 for x in cps] # 4.7 is the average length of a word
    return wpm

keyboard_pos = {}
keyboard_rows = [
    ["~`",  "1!", "2@", "3#", "4$", "5%", "6^", "7&", "8*", "9(", "0)", "-_", "=+"],
    ["qQ", "wW", "eE", "rR", "tT", "yY", "uU", "iI", "oO", "pP", "[{", "]}", "\\|"],
    ["aA", "sS", "dD", "fF", "gG", "hH", "jJ", "kK", "lL", ";:", "'\""],
    ["zZ", "xX", "cC", "vV", "bB", "nN", "mM", ",<", ".>", "/?"]
]
keyboard_row_offsets = [
    0, 1.5, 1.75, 2.1
]
key_space = 0.1
row_space = 1.1
for i, (row, offset) in enumerate(list(zip(keyboard_rows, keyboard_row_offsets))[::-1]):
    for k, keys in enumerate(row):
        keyboard_pos[keys] = (offset + k*(1 + key_space) + 0.5, i*row_space)

def get_keyboard_plot(timetable): # returns the filename of the image in temp/
    incorrect_freq = {}
    max_incorrect = 0
    for [_, stamp] in timetable:
        if not stamp["correct"]:
            incorrect_freq.setdefault(stamp["key"], 0)
            incorrect_freq[stamp["key"]] += 1
            max_incorrect = max(max_incorrect, incorrect_freq[stamp["key"]])
    plt.style.use("seaborn-v0_8-ticks")
    fig, ax = plt.subplots()
    xs, ys = [], []
    keyboard_c = []
    for keys, (x, y) in keyboard_pos.items():
        keyboard_c.append(256 * (incorrect_freq.get(keys[0], 0)+incorrect_freq.get(keys[1], 0)) / max_incorrect)
        xs.append(x)
        ys.append(y)
    ax.scatter(xs, ys, marker='s', edgecolors='black', c=keyboard_c, cmap=cm.get_cmap("YlOrRd"))
    ax.set(ylim=(-2, 5.5))
    for keys, xy in keyboard_pos.items():
        ax.annotate(keys[0], xy=np.array(xy) + np.array([0.3, 0]))
        ax.annotate(keys[1], xy=np.array(xy) + np.array([0.3, 0.3]))
    add_k_means_clustering(ax, zip(xs, ys))
    plt.axis('off')
    filename = "keyboard-plot-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    plt.savefig("temp/" + filename, dpi=300, bbox_inches='tight')
    plt.close()
    return filename

def add_k_means_clustering(ax, data):
    kmeans_model = KMeans(n_clusters=2, n_init="auto")
    kmeans_model.fit_predict(np.array(list(data)))
    centroids = kmeans_model.cluster_centers_
    for centroid in centroids:
        circle = Ellipse(xy=centroid, width=0.5 * 5, height=0.32 * 5, color='r', alpha = 0.3)
        ax.add_patch(circle)