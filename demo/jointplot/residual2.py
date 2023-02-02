try:
    import numpy as np
except ImportError:
    np = None

try:
    import pandas as pd
except ImportError:
    pd = None

from lets_plot.plot.core import PlotSpec, aes
from lets_plot.plot.geom import *
from lets_plot.plot.label import ylab
from lets_plot.plot.marginal_layer import ggmarginal
from lets_plot.plot.theme_ import *

__all__ = ['residual_plot']


_METHOD_DEF = "lm"
_METHOD_LM_DEG_DEF = 1
_METHOD_LOESS_SPAN_DEF = .5
_GEOM_DEF = "point"
_BINS_DEF = 30
_MARGINAL_DEF = "dens:r"
_COLOR_DEF = "#118ed8"
_HLINE_DEF = True
_RESIDUAL_COL = "..residual.."


def _extract_data_series(df, x, y):
    xs = np.array(df[x])
    ys = np.array(df[y])
    if xs.size != ys.size:
        raise Exception("All data series in dataset must have equal size "
                        "{x_col} : {x_len} {y_col} : {y_len}".format(
            x_col=x,
            y_col=y,
            x_len=xs.size,
            y_len=ys.size
        ))
    if xs.size == 1:
        raise Exception("Data should have at least two points.")

    return xs, ys

def _poly_transform(deg):
    def _transform(X):
        assert len(X.shape) > 1 and X.shape[1] == 1
        return np.concatenate([np.power(X, d) for d in range(deg + 1)], axis=1).astype(float)

    return _transform

def _get_lm_predictor(xs_train, ys_train, deg):
    import statsmodels.api as sm

    X_train = xs_train.reshape(-1, 1)
    transform = _poly_transform(deg)
    model = sm.OLS(ys_train, transform(X_train)).fit()

    return lambda xs: model.predict(transform(xs.reshape(-1, 1)))

def _get_loess_predictor(xs_train, ys_train, span, seed, max_n):
    import statsmodels.api as sm
    from scipy.interpolate import interp1d

    if max_n is not None:
        np.random.seed(seed)
        indices = np.random.choice(range(xs_train.size), size=max_n, replace=False)
        xs_train = xs_train[indices]
        ys_train = ys_train[indices]
    lowess = sm.nonparametric.lowess(ys_train, xs_train, frac=span)
    lowess_x = list(zip(*lowess))[0]
    lowess_y = list(zip(*lowess))[1]
    model = interp1d(lowess_x, lowess_y, bounds_error=False)

    return lambda xs: np.array([model(x) for x in xs])

def _get_predictor(xs_train, ys_train, method, deg, span, seed, max_n):
    if method == 'lm':
        return _get_lm_predictor(xs_train, ys_train, deg)
    if method in ['loess', 'lowess']:
        return _get_loess_predictor(xs_train, ys_train, span, seed, max_n)
    if method == 'none':
        return lambda xs: np.array([0] * xs.size)
    else:
        raise Exception("Unknown method '{0}'".format(method))

def _get_stat_data(data, x, y, group_by, method, deg, span, seed, max_n):
    def _get_group_stat_data(group_df):
        xs, ys = _extract_data_series(group_df, x, y)
        if len(xs) == 0:
            return group_df.assign(**{_RESIDUAL_COL: []}), xs, ys
        predictor = _get_predictor(xs, ys, method, deg, span, seed, max_n)
        return group_df.assign(**{_RESIDUAL_COL: ys - predictor(xs)}), xs, ys

    df = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    df = df[(df[x].notna()) & df[y].notna()]
    if group_by is None:
        return _get_group_stat_data(df)
    else:
        df_list, xs_list, ys_list = zip(*[
            _get_group_stat_data(df[df[group_by] == group_value])
            for group_value in df[group_by].unique()
        ])
        return pd.concat(df_list), np.concatenate(xs_list), np.concatenate(ys_list)

def _get_binwidth(xs, ys, binwidth, bins):
    if binwidth is not None or bins is not None or len(xs) == 0:
        return binwidth
    binwidth_x = (xs.max() - xs.min()) / _BINS_DEF
    binwidth_y = (ys.max() - ys.min()) / _BINS_DEF
    binwidth_max = max(binwidth_x, binwidth_y)

    return [binwidth_max, binwidth_max]

def _parse_marginal(marginal, color, color_by, show_legend, bins2d, binwidth2d):
    def _parse_marginal_layer(geom_name, side, size):
        layer = None
        if geom_name in ["dens", "density"]:
            layer = geom_density(color=color, show_legend=show_legend)
        elif geom_name in ["hist", "histogram"]:
            bins = None if bins2d is None else (bins2d[0] if side in ["t", "b"] else bins2d[1])
            binwidth = None if binwidth2d is None else (binwidth2d[0] if side in ["t", "b"] else binwidth2d[1])
            marginal_color = None if color_by is not None else (color or _COLOR_DEF)
            layer = geom_histogram(color=marginal_color, alpha=0, bins=bins, binwidth=binwidth, show_legend=show_legend)
        elif geom_name in ["box", "boxplot"]:
            layer = geom_boxplot(color=color, show_legend=show_legend)
        else:
            raise Exception("Unknown geom '{0}'".format(geom_name))

        return ggmarginal(side, size=size, layer=layer)

    marginals = []
    for layer_description in filter(bool, marginal.split(",")):
        params = layer_description.strip().split(":")
        geom_name, sides = params[0], params[1]
        size = float(params[2]) if len(params) > 2 else None
        for side in sides:
            marginals.append(_parse_marginal_layer(geom_name, side, size))

    return marginals


def residual_plot(data=None, x=None, y=None, *,
                  method=_METHOD_DEF,
                  deg=_METHOD_LM_DEG_DEF,
                  span=_METHOD_LOESS_SPAN_DEF, seed=None, max_n=None,
                  geom=_GEOM_DEF,
                  bins=None, binwidth=None,
                  color=None, size=None, alpha=None,
                  color_by=None,
                  show_legend=None,
                  hline=_HLINE_DEF, marginal=_MARGINAL_DEF):
    # requirements
    if np is None:
        raise ValueError("Module 'numpy' is required for residual plot")
    if pd is None:
        raise ValueError("Module 'pandas' is required for residual plot")
    # prepare data
    stat_data, xs, ys = _get_stat_data(data, x, y, color_by, method, deg, span, seed, max_n)
    # prepare parameters
    if isinstance(bins, int):
        bins = [bins, bins]
    if isinstance(binwidth, int) or isinstance(binwidth, float):
        binwidth = [binwidth, binwidth]
    binwidth = _get_binwidth(xs, ys, binwidth, bins)
    # prepare mapping
    mapping_dict = {'x': x, 'y': _RESIDUAL_COL}
    if color_by is not None:
        mapping_dict['color'] = color_by
    # prepare scales
    scales = []
    if method == 'none':
        scales.append(ylab(y))
    else:
        scales.append(ylab("{0} residual".format(y)))
    # prepare layers
    layers = []
    # main layer
    if geom == 'point':
        layers.append(geom_point(color=color, size=size, alpha=alpha, show_legend=show_legend))
    elif geom == 'contour':
        layers.append(geom_density2d(
            color=color, alpha=alpha,
            show_legend=show_legend
        ))
    elif geom == 'tile':
        layers.append(geom_bin2d(
            bins=bins, binwidth=binwidth,
            color=color, size=size, alpha=alpha,
            show_legend=show_legend
        ))
    elif geom == 'none':
        pass
    else:
        raise Exception("Unknown geom '{0}'".format(geom))
    # hline layer
    if hline:
        layers.append(geom_hline(yintercept=0, color="magenta", linetype='dashed'))
    # marginal layers
    if marginal != 'none':
        layers += _parse_marginal(marginal, color, color_by, show_legend, bins, binwidth)
    # theme layer
    theme_layer = theme(axis="blank",
                        axis_text_x=element_text(),
                        axis_title_x=element_text(),
                        axis_line_y=element_line(),
                        axis_ticks_y=element_line(),
                        axis_text_y=element_text(),
                        axis_title_y=element_text())

    return PlotSpec(data=stat_data, mapping=aes(**mapping_dict), scales=scales, layers=layers) + theme_layer