from lets_plot.plot.core import PlotSpec, aes
from lets_plot.plot.geom import geom_smooth
from lets_plot.plot.label import xlab, ylab
from lets_plot.plot.theme_set import theme_classic

from common import *
from residual import *

__all__ = ['joint_plot']


_GEOM_DEF = 'point'


def _get_geom(geom_kind):
    replaces = {'reg': 'point'}
    return replaces[geom_kind] if geom_kind in replaces.keys() else geom_kind

def _get_marginal_def(geom_kind, color_by=None):
    if geom_kind == 'reg':
        return "hist:tr,dens:tr"
    if geom_kind == 'density2df':
        return "area:tr"
    if geom_kind  == 'density2d' or color_by is not None:
        return "dens:tr"
    return "hist:tr"


def joint_plot(data, x, y, *,
               geom=None,
               bins=None, binwidth=None,
               color=None, size=None, alpha=None,
               color_by=None,
               show_legend=None,
               marginal=None):
    # prepare parameters
    geom_kind = geom or _GEOM_DEF
    binwidth2d, bins2d = _get_bin_params_2d(data[x], data[y], binwidth, bins)
    # prepare mapping
    mapping_dict = {'x': x, 'y': y}
    if color_by is not None:
        mapping_dict['color'] = color_by
    # prepare layers
    layers = []
    # main layer
    main_layer = _get_geom2d_layer(_get_geom(geom_kind), binwidth2d, bins2d, color, color_by, size, alpha, show_legend)
    if main_layer is not None:
        layers.append(main_layer)
    # smooth layer
    if geom == 'reg':
        layers.append(geom_smooth())
    # marginal layers
    if len(data[x]) == 0:
        marginal = 'none'
    defined_marginal = marginal or _get_marginal_def(geom_kind, color_by)
    if defined_marginal != 'none':
        layers += _get_marginal_layers(defined_marginal, binwidth2d, bins2d, color, color_by, show_legend)
    # theme layer
    theme_layer = theme_classic()

    return PlotSpec(data=data, mapping=aes(**mapping_dict), scales=[xlab(x), ylab(y)], layers=layers) + theme_layer