from lets_plot.plot.core import aes
from lets_plot.plot.geom import *
from lets_plot.plot.marginal_layer import ggmarginal

__all__ = ['_get_bin_params_2d', '_get_geom2d_layer', '_get_marginal_layers']


_BINS_DEF = 30
_COLOR_DEF = "#118ed8"

_MARGINAL_HIST_FILL = "white"


def _get_bin_params_2d(xs, ys, binwidth, bins):
    if isinstance(bins, int):
        bins = [bins, bins]
    if isinstance(binwidth, int) or isinstance(binwidth, float):
        binwidth = [binwidth, binwidth]
    if binwidth is not None or bins is not None or len(xs) == 0:
        return binwidth, bins
    binwidth_x = (max(xs) - min(xs)) / _BINS_DEF
    binwidth_y = (max(ys) - min(ys)) / _BINS_DEF
    binwidth_max = max(binwidth_x, binwidth_y)

    return [binwidth_max, binwidth_max], bins

def _get_geom2d_layer(geom_kind, binwidth2d, bins2d, color, color_by, size, alpha, show_legend):
    if geom_kind == 'point':
        return geom_point(color=color, size=size, alpha=alpha, show_legend=show_legend)
    if geom_kind == 'tile':
        return geom_bin2d(
            bins=bins2d, binwidth=binwidth2d,
            color=color, size=size, alpha=alpha,
            show_legend=show_legend
        )
    if geom_kind == 'density2d':
        return geom_density2d(
            aes(color=('..group..' if color_by is None else color_by)),
            color=color, size=size, alpha=alpha,
            show_legend=show_legend
        )
    if geom_kind == 'density2df':
        return geom_density2df(
            aes(fill=('..group..' if color_by is None else color_by)),
            color=color, size=size, alpha=alpha,
            show_legend=show_legend
        )
    if geom_kind == 'none':
        return None
    raise Exception("Unknown geom '{0}'".format(geom_kind))

def _get_marginal_layers(marginal, binwidth2d, bins2d, color, color_by, show_legend):
    def _get_marginal_layer(geom_kind, side, size):
        layer = None
        if geom_kind in ['dens', 'density']:
            layer = geom_density(color=color, show_legend=show_legend)
        elif geom_kind in ['area']:
            marginal_aes = aes(fill=color_by) if color_by is not None else None
            marginal_fill = color if marginal_aes is None else None
            layer = geom_area(marginal_aes, stat='density', fill=marginal_fill, show_legend=show_legend)
        elif geom_kind in ['hist', 'histogram']:
            binwidth = None if binwidth2d is None else (binwidth2d[0] if side in ['t', 'b'] else binwidth2d[1])
            bins = None if bins2d is None else (bins2d[0] if side in ['t', 'b'] else bins2d[1])
            marginal_color = None if color_by is not None else (color or _COLOR_DEF)
            layer = geom_histogram(color=marginal_color, fill=_MARGINAL_HIST_FILL, bins=bins, binwidth=binwidth, show_legend=show_legend)
        elif geom_kind in ['box', 'boxplot']:
            layer = geom_boxplot(color=color, show_legend=show_legend)
        else:
            raise Exception("Unknown geom '{0}'".format(geom_kind))

        return ggmarginal(side, size=size, layer=layer)

    marginals = []
    for layer_description in filter(bool, marginal.split(",")):
        params = layer_description.strip().split(":")
        geom_kind, sides = params[0], params[1]
        size = float(params[2]) if len(params) > 2 else None
        for side in sides:
            marginals.append(_get_marginal_layer(geom_kind, side, size))

    return marginals