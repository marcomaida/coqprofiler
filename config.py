PROFILE_FOLDER = "raw"             # Temporary raw file directory
CHARS_PER_LINE = 60                # Maximum number of character shown per line in the plot

SKIP_COQC = False                  # False => Run coqc          | True => Use the last raw results in the PROFILE_FILE
OUTPUT_TO_FILE = True              # False => Show a UI         | True => Output a file in the same directory with the same name
SHOW_TOP_N_LINES = 300             # N<=0  => Apply no filter   | N>0  => Keep only the N lines that took the largest time
FILTER_ZERO_SECONDS_LINES = True   # False => Apply no filter   | True => Filter lines whose compiling time is zero
SAVE_DATAFRAME = True              # False => Do nothing        | True => Save the dataframe in a CSV file
# Figure size for file output
BASIC_WIDTH = 3
EXTRA_WIDTH_PER_CHARACTER = 0.08
BASIC_HEIGHT = 1
EXTRA_HEIGHT_PER_LINE = 0.1