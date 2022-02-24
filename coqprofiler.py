#!/usr/bin/env python3
import os, sys, subprocess, re, argparse
from config import *
import matplotlib.pyplot as plt, seaborn as sb, pandas as pd
from matplotlib import rcParams
from matplotlib.widgets import Slider

###### Parsing command line input
parser = argparse.ArgumentParser(description="Profiling Coq Time")
parser.add_argument('input', help='Input file.')
known_args, extra_args = parser.parse_known_args()
input = known_args.input
coq_args = [arg for arg in extra_args]

###### Running coqc with -time and outputting to a file
if SKIP_COQC:
    print("Skipping Coq compilation...")
else:
    command = ["coqc", input] + coq_args
    if '-time' not in command: command += ['-time']
    if not os.path.exists(os.path.dirname(PROFILE_FILE)): 
        os.makedirs(os.path.dirname(PROFILE_FILE))

    with open(PROFILE_FILE, "w") as outfile:
        print("Running Coq...\n> " + " ".join(command)+"\n")
        r = subprocess.run(command, stdout=outfile)

    if r.returncode != 0:
        print("\nCoq failed. Aborting...")
        sys.exit(1)

###### Parsing profile text file
with open(PROFILE_FILE) as file:
    profile_lines = file.readlines()
with open(input) as f:
    coq_file = f.read()

instr_re = re.compile("\[(.*)\]")
chars_s_re = re.compile("Chars (.*) - (.*) \[") # Chars 564 - 1553 [...
time_re = re.compile("] (.*) secs")

data = []
for i,l in enumerate(profile_lines):
    time = float(time_re.search(l).group(1))
    instr = instr_re.search(l).group(1)
    chars_search = chars_s_re.search(l)
    charsl = int(chars_search.group(1))
    charsr = int(chars_search.group(2))
    chars = f' ({charsl}-{charsr})'
    line = coq_file[:charsl].count("\n")+1

    line_l = f"{line}: "
    line_instr = coq_file[charsl-1:charsr].replace("\n"," ")[:CHARS_PER_LINE]
    cert = line_l + line_instr.ljust(CHARS_PER_LINE)

    if len(data) > 0 and line == data[-1][0]: # Group together if same line
        data[-1][1] += ", " + chars
        # if len(data[-1][2]) < CHARS_PER_LINE:
        #     data[-1][2] += cert
        data[-1][3] += time
    else:
        data += [[line,chars, cert, time]]

df = pd.DataFrame(data, columns=["line","chars","cert","time"])
total_time = df["time"].sum()
if FILTER_ZERO_SECONDS_LINES:
    df = df[df.time > 0]
if SHOW_TOP_N_LINES > 0:
    df = df.nlargest(SHOW_TOP_N_LINES, "time")


##### Plotting
sb.set(rc={'axes.facecolor':'white', 'figure.facecolor':'white'})
if OUTPUT_TO_FILE:
    plt.figure(figsize=(BASIC_WIDTH  + EXTRA_WIDTH_PER_CHARACTER * CHARS_PER_LINE, 
                        BASIC_HEIGHT + EXTRA_HEIGHT_PER_LINE     * df.shape[0]    ))
ax = sb.barplot(data=df, y="line", x="time", orient="h")
ax.set_yticklabels(df['cert'], fontdict = {'family': 'monospace', 'size':'7' })
ax.bar_label(ax.containers[0], fontsize=6)
plt.tight_layout()

plt.xlabel("seconds")
plt.ylabel("Line")
plt.title(f"Profiling data of {input} (total: {total_time} sec)", fontsize=5)

if OUTPUT_TO_FILE:
    out_path = os.path.join(os.path.dirname(input), f"{os.path.basename(input)}.pdf")
    plt.savefig(out_path)
else:
    ###### Showing interface with sliders
    line_numbers = list(df["line"])
    nlines = len(line_numbers)
    min_line, max_line = min(line_numbers), max(line_numbers)
    max_time = max(df["time"])
    spos = Slider(plt.axes([0.1, 0.05, 0.4, 0.03], facecolor='lightgoldenrodyellow'), 
                'Start', min_line, max_line, valstep=df["line"],
                valinit=line_numbers[0])
    srange = Slider(plt.axes([0.1, 0.01, 0.4, 0.03], facecolor='lightgoldenrodyellow'), 
                'Lines', min(10, nlines), nlines, valstep=1,
                valinit=min(30, nlines))
    def update(_=None):
        n = line_numbers.index(spos.val)
        end_line = min(n+srange.val, nlines)
        start_line = max(0, end_line-srange.val)
        ax.set_ylim(end_line, start_line)
    spos.on_changed(update)
    srange.on_changed(update)
    update()

    plt.get_current_fig_manager().set_window_title(f"Profiling data of {input}")
    plt.show()
