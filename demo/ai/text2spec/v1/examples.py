import pandas as pd

from lets_plot import *

def dump_plot(plot, display=None):
    import json
    from lets_plot._type_utils import standardize_dict
    return json.dumps(standardize_dict(plot.as_dict()))

class Example:
    def __init__(self, query, plot):
        self.request = query
        self.response = dump_plot(plot)

class Examples:
    _mpg_df = pd.read_csv("https://raw.githubusercontent.com/JetBrains/lets-plot-docs/refs/heads/master/data/mpg.csv")

    def p1(self):
        query = "Plot of function y = x^2 from -3 to 3."
        data = {'a': [-3, -2, -1, 0, 1, 2, 3], 'b': [9, 4, 1, 0, 1, 4, 9]}
        plot = ggplot(data, aes('a', 'b')) + geom_line()
        return Example(query, plot)

    def p2(self):
        query = "Scatter plot of the following data: {'X': [0, 1, 2, 3], 'Y': [1.1, 2.4, -1.0, 2.8]}."
        data = {'X': [0, 1, 2, 3], 'Y': [1.1, 2.4, -1.0, 2.8]}
        plot = ggplot(data, aes('X', 'Y')) + geom_point()
        return Example(query, plot)

    def p3(self):
        query = 'Bar plot on the values ["A", "B", "C", "A", "A", "C"].'
        data = {'v': ["A", "B", "C", "A", "A", "C"]}
        plot = ggplot(data) + geom_bar(aes(x='v'))
        return Example(query, plot)

    def p4(self):
        query = "ECDF plot on the values [1, 1.2, -.5, 1.3]."
        data = {'v': [1, 1.2, -.5, 1.3]}
        plot = ggplot() + stat_ecdf(aes(x='v'), data=data)
        return Example(query, plot)

    def p5(self):
        query = "Use mpg dataset. Draw a count plot of fl vs. drv with class mapped to color and with facetting by class."
        df = self._mpg_df[["fl", "drv", "class"]].iloc[:20].copy()
        plot = ggplot(df, aes("fl", "drv")) + \
            geom_count(aes(color="class")) + \
            facet_grid(x="class")
        return Example(query, plot)

    def p6(self):
        query = """
Dataset is mpg.
Draw a plot with two layers: point and smooth.
Variables: cty vs. hwy.
Both layers should be colored by drv.
Also use brewer color scale with 'Set2' palette.
        """.strip().replace("\n", " ")
        df = self._mpg_df[["cty", "hwy", "drv"]].iloc[:10].copy()
        plot = ggplot(df, aes("cty", "hwy")) + \
            geom_point(aes(color="drv")) + \
            geom_smooth(aes(color="drv")) + \
            scale_color_brewer(palette='Set2')
        return Example(query, plot)

examples = Examples()
EXAMPLES = [getattr(examples, method)() for method in dir(examples) if not method.startswith("_")]