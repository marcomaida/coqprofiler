#!/usr/bin/env python3
from config import *
import os, sys, subprocess, re, argparse
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
from matplotlib import rcParams
from matplotlib.widgets import Slider

###### Parsing command line input
parser = argparse.ArgumentParser(description="Profiling Coq Time")
parser.add_argument('input', help='Input file.')
known_args, extra_args = parser.parse_known_args()
input = known_args.input
coq_args = [arg for arg in extra_args]

###### Deciding output file names and paths
input_folder = os.path.dirname(input)
input_basename = os.path.splitext(os.path.basename(input))[0]
if SAVE_RAW_FILE:
    profile_txt_name = os.path.join(input_folder, f"{input_basename}.txt")
else:
    profile_txt_name = os.path.join(PROFILE_FOLDER, f"{input_basename}.txt")
profile_csv_name = os.path.join(input_folder, f"{input_basename}.csv")
profile_pdf_name = os.path.join(input_folder, f"{input_basename}.pdf")

###### Running coqc with -time and outputting to a file
if SKIP_COQC:
    print("Skipping Coq compilation...")
else:
    command = ["coqc", input] + coq_args
    if '-time' not in command: command += ['-time']
    if not os.path.exists(os.path.dirname(profile_txt_name)): 
        os.makedirs(os.path.dirname(profile_txt_name))

    with open(profile_txt_name, "w") as outfile:
        print("Running Coq...\n> " + " ".join(command)+"\n")
        r = subprocess.run(command, stdout=outfile)

    if r.returncode != 0:
        print("\nCoq failed. Aborting...")
        sys.exit(1)

###### Parsing profile text file
with open(profile_txt_name) as file:
    profile_lines = file.readlines()
with open(input) as f:
    coq_file = f.read()

instr_re = re.compile("\[(.*)\]")
chars_s_re = re.compile("Chars (.*) - (.*) \[") # Chars 564 - 1553 [...
time_re = re.compile("] (.*) secs")

data = []
for i,l in enumerate(profile_lines):
    search = time_re.search(l)
    if search is None or search.group(1) is None: continue
    time = float(search.group(1))
    instr = instr_re.search(l).group(1)
    chars_search = chars_s_re.search(l)
    charsl = int(chars_search.group(1))
    charsr = int(chars_search.group(2))
    chars = f' ({charsl}-{charsr})'
    line = coq_file[:charsl].count("\n")+1
    line_instr = coq_file[charsl-1:charsr].replace("\n"," ")

    if len(data) > 0 and line == data[-1][0]: # Group together if same line
        data[-1][1] += ", " + chars
        data[-1][2] += line_instr
        data[-1][3] += time
    else:
        data += [[line, chars, line_instr, time]]

# Formal line with line number and maximum chars
for l in data:
    l[2] = f"{l[0]}: {l[2][:CHARS_PER_LINE].ljust(CHARS_PER_LINE)}"

df = pd.DataFrame(data, columns=["line","chars","cert","time"])
total_time = df["time"].sum()

if SAVE_DATAFRAME:
    print(f"Saving dataframe to {profile_csv_name}...")
    df.to_csv(profile_csv_name)

if FILTER_ZERO_SECONDS_LINES:
    df = df[df.time > 0]
if SHOW_TOP_N_LINES > 0:
    df = df.nlargest(SHOW_TOP_N_LINES, "time")
    df = df.sort_values(by=["line"])


##### Plotting
sb.set(rc={'axes.facecolor':'white', 'figure.facecolor':'white'})
if SAVE_PLOT:
    plt.figure(figsize=(BASIC_WIDTH  + EXTRA_WIDTH_PER_CHARACTER * CHARS_PER_LINE, 
                        BASIC_HEIGHT + EXTRA_HEIGHT_PER_LINE     * df.shape[0]    ))
ax = sb.barplot(data=df, y="line", x="time", orient="h")
ax.set_yticklabels(df['cert'], fontdict = {'family': 'monospace', 'size':'7' })
ax.bar_label(ax.containers[0], fontsize=6)
plt.tight_layout()

plt.xlabel("seconds")
plt.ylabel("Line")

title = f"Profiling data of {input} (total: {total_time:.0f} sec"
if SHOW_TOP_N_LINES > 0:
    title += f"; showing {SHOW_TOP_N_LINES} lines"
if FILTER_ZERO_SECONDS_LINES:
    title += "; filtering 0 seconds lines"
title += ")"

plt.title(title, fontsize=5)

if SAVE_PLOT:
    print(f"Saving figure to {profile_pdf_name}...")
    plt.savefig(profile_pdf_name)
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
