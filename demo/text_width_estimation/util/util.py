from collections import namedtuple

import numpy as np
import pandas as pd

from lets_plot import *
LetsPlot.setup_html()

Font = namedtuple("Font", ["family", "size", "face"])

FONT_FAMILIES = {
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
        "Lucida Console",
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
        "Lucida Console",
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
    result_df = result_df[result_df.font_family.isin(FONT_FAMILIES[df_type])].reset_index(drop=True)
    result_df.fillna("", inplace=True)

    return result_df

def filter_by_font(df, font, *, filters=["family", "size", "face"], drop=True):
    result_df = df.copy()
    if "family" in filters:
        result_df = result_df[result_df.font_family == font.family]
    if "size" in filters:
        result_df = result_df[result_df.font_size == font.size]
    if "face" in filters:
        result_df = result_df[result_df.font_face == font.face]
    if drop:
        result_df = result_df.drop(columns=["font_{0}".format(f) for f in filters]).reset_index(drop=True)
    return result_df

def get_char_weights_df(char_widths_df, control_df, *, font):
    def occurrences_number(series, symbol):
        try:
            s = series.str.count(symbol).sum()
            return s - series.size if symbol in ['$', '^'] else s
        except:
            return 0
    font_char_widths_df = filter_by_font(char_widths_df, font)[["alphabet", "char", "width"]]\
        .drop_duplicates(subset=["char"]).set_index("char")
    texts_s = control_df.text.drop_duplicates().str[0:-1]
    char_weights_s = pd.Series({c: occurrences_number(texts_s, c)
                                for c in font_char_widths_df.index}, name="weight") + 1
    return pd.concat([font_char_widths_df, char_weights_s], axis="columns")

def transform_values_to_orders(df, *, values_col, sorted_col, grouping_cols=[], agg_method=np.mean):
    def as_tuple(t):
        if isinstance(t, str):
            return (t,)
        return t

    def slice_df(sliced_df, group_names, group_values):
        if len(group_names) == 0:
            return sliced_df
        return slice_df(sliced_df[sliced_df[group_names[0]] == group_values[0]], group_names[1:], group_values[1:])

    def get_row_df(group_df):
        group_df = group_df.groupby(sorted_col)[values_col].agg(agg_method).reset_index()
        if group_df[values_col].min() == group_df[values_col].max():
            return group_df.assign(result=lambda x: np.nan).set_index(sorted_col).result
        group_df = group_df.sort_values(by=values_col)
        group_df["result"] = group_df.assign(u=1)\
                                     .groupby(values_col)["u"]\
                                     .transform(lambda x: (x.cumsum() / x.count()).astype(int) * x.count())\
                                     .cumsum()\
                                     .shift(periods=1, fill_value=0)
        return group_df.set_index(sorted_col).result

    if len(grouping_cols) == 0:
        return get_row_df(df).to_frame("order").T

    result_df = pd.concat([
        get_row_df(
            slice_df(df, grouping_cols, as_tuple(t))
        ).to_frame(name=as_tuple(t)).T
        for t in df.groupby(grouping_cols)[values_col].max().index
    ])
    result_index = pd.MultiIndex.from_tuples(result_df.index, names=grouping_cols) \
        if len(grouping_cols) > 1 else result_df.index
    result_df.set_index(result_index, inplace=True)

    return result_df

def transform_char_widths_to_orders(cw_df):
    return pd.concat([
        transform_values_to_orders(
            cw_df[cw_df.alphabet == alphabet],
            values_col="width",
            sorted_col="char",
            grouping_cols=["font_family", "font_size", "font_face"]
        )
        for alphabet in cw_df.alphabet.unique()
    ], keys=cw_df.alphabet.unique(), names=["alphabet"], axis=1)