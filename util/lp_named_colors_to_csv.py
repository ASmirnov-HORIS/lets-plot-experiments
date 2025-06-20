#!/usr/bin/env python

from argparse import ArgumentParser
import urllib.request

import pandas as pd

DEF_OUTPUT_FILEPATH = "lp_named_colors.csv"

COLOR_NAMES_URL = "https://raw.githubusercontent.com/JetBrains/lets-plot/3f742eba1b5d214a9c3ca070abb4eab269ce88c0/commons/src/commonMain/kotlin/org/jetbrains/letsPlot/commons/values/Colors.kt"
COLOR_HEX_CODES_URL = "https://raw.githubusercontent.com/JetBrains/lets-plot/3f742eba1b5d214a9c3ca070abb4eab269ce88c0/commons/src/commonMain/kotlin/org/jetbrains/letsPlot/commons/values/Color.kt"

def _read_color_names():
    start_read = False
    color_names = {}
    with urllib.request.urlopen(COLOR_NAMES_URL) as response:
        for line in response:
            code = line.decode("utf-8").strip()
            if code.startswith("private val baseColors"):
                start_read = True
            elif start_read and code.startswith(")"):
                break
            elif start_read:
                color_name = code.split('"')[1]
                color_id = code.split(' ')[-1].replace("Color.", "").replace(",", "")
                if color_id != "TRANSPARENT":
                    color_names[color_name] = color_id
            else:
                continue
    return color_names

def _read_color_hex_codes():
    start_read = False
    color_hex_codes = {}
    with urllib.request.urlopen(COLOR_HEX_CODES_URL) as response:
        for line in response:
            code = line.decode("utf-8").strip()
            if code.startswith("companion object"):
                start_read = True
            elif start_read and code == "":
                break
            elif start_read:
                color_id = code.split(' ')[1]
                color_hex_code = code.split(' ')[-1].replace('parseHex("', "").replace('")', "")
                if color_id != "TRANSPARENT":
                    color_hex_codes[color_id] = color_hex_code
            else:
                continue
    return color_hex_codes

def build_csv(filepath):
    color_names = _read_color_names()
    color_hex_codes = _read_color_hex_codes()
    correspondence = {name: color_hex_codes[id] for name, id in color_names.items()}
    df = pd.DataFrame.from_dict(correspondence, orient="index").reset_index()
    df.columns = ["name", "hex"]
    df.to_csv(filepath, index=False)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-o", "--output", default=DEF_OUTPUT_FILEPATH, metavar='OUTPUT',
                        help="Path to the csv file with result.")
    args = parser.parse_args()
    build_csv(args.output)