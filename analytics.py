import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np

def get_wpm(timetable):
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
        for key in keys:
            keyboard_pos[key] = (offset + k*(1 + key_space) + 0.5, i*row_space)
keyboard_c = np.linspace(0, 1, len(keyboard_pos))

def get_keyboard_plot(timetable):
    plt.style.use("seaborn-v0_8-ticks")
    fig, ax = plt.subplots()
    xs, ys = [], []
    for x, y in keyboard_pos.values():
        xs.append(x)
        ys.append(y)
    ax.scatter(xs, ys, marker='s', c=keyboard_c, cmap=cm.get_cmap("Pastel1"))
    xy_offsets = {}
    ax.set(ylim=(-2, 5.5))
    for chars, xy in keyboard_pos.items():
        if xy not in xy_offsets.keys():
            xy_offsets[xy] = np.array([0.3, 0], 'float64')
        ax.annotate(chars, xy=np.array(xy) + xy_offsets[xy])
        xy_offsets[xy] += np.array([0, 0.3])
    plt.axis('off')
    plt.show()
    # plt.savefig("test.png", bbox_inches='tight')