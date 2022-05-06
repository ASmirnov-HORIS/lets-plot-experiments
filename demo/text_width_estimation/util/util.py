import numpy as np
import pandas as pd

from lets_plot import *
LetsPlot.setup_html()

FONT_FACES = {
    "train": [
        "Courier",
        "Geneva",
        "Georgia",
        "Helvetica",
        "Lucida Grande",
        "Times New Roman",
        "Verdana",
    ],
    "test": [
        "Arial",
        "Brush Script MT",
        "Lucida Console",
        "Wingdings",
    ],
    "all": [
        "Courier",
        "Geneva",
        "Georgia",
        "Helvetica",
        "Lucida Grande",
        "Times New Roman",
        "Verdana",
        "Arial",
        "Brush Script MT",
        "Lucida Console",
        "Wingdings",
    ],
}

def plot_matrix(plots=[], width=400, height=300, columns=2):
    bunch = GGBunch()
    for i in range(len(plots)):
        row = int(i / columns)
        column = i % columns
        bunch.add_plot(plots[i], column * width, row * height, width, height)
    return bunch.show()

def get_df(path, df_type):
    result_df = pd.read_csv(path)
    result_df = result_df[result_df.font_face.isin(FONT_FACES[df_type])].reset_index(drop=True)
    result_df.fillna("", inplace=True)

    return result_df

def transform_char_widths_to_orders(char_widths_df):
    def get_row_df(font_df, alphabet):
        font_df = font_df[font_df.alphabet == alphabet]
        if font_df.width.min() == font_df.width.max():
            return font_df.assign(result=lambda x: np.nan).set_index(["alphabet", "char"]).result

        font_df = font_df.sort_values(by="width")
        font_df["result"] = font_df.assign(u=1)\
                                   .groupby("width")["u"]\
                                   .transform(lambda x: (x.cumsum() / x.count()).astype(int) * x.count())\
                                   .cumsum()\
                                   .shift(periods=1, fill_value=0)

        return font_df.set_index(["alphabet", "char"]).result

    result_df = pd.concat([
        pd.concat([
            get_row_df(
                char_widths_df[
                    (char_widths_df.font_face == t[0])&
                    (char_widths_df.font_size == t[1])&
                    (char_widths_df.font_version == t[2])
                ],
                alphabet
            ) for alphabet in char_widths_df.alphabet.unique()
        ]).to_frame(name=t).T
        for t in char_widths_df.groupby(["font_face", "font_size", "font_version"]).width.max().index
    ])
    result_df.set_index(pd.MultiIndex.from_tuples(result_df.index, names=("font_face", "font_size", "font_version")), inplace=True)

    return result_df