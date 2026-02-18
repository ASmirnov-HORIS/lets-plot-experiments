from lets_plot import *

def _dodged_coord(group_id, subgroup_id, subgroup_count, width):
    median = (subgroup_count - 1) / 2
    offset = (subgroup_id - median) * width
    scaler = 1.0 / subgroup_count
    return group_id + offset * scaler

def geom_bracket2(mapping=None, *, data=None,
                  subgroup1=None, subgroup2=None,               # column names for subgroups
                  dodge_width=None,                             # should be the same as width parameter in the position_dodge()
                  ordered_groups=None, ordered_subgroups=None,  # explicit order for group/subgroup indices
                  position=None, show_legend=None,
                  manual_key=None,
                  sampling=None,
                  orientation=None,
                  label_format=None, na_text=None,
                  nudge_x=None, nudge_y=None, nudge_unit=None,
                  size_unit=None,
                  bracket_shorten=None, tip_length_unit=None,
                  color_by=None,
                  **other_args):
    mapping_dict = mapping.as_dict()
    x_aes = mapping_dict["x"]
    if not x_aes:
        return geom_bracket(mapping=mapping,
                            data=data,
                            position=position,
                            show_legend=show_legend,
                            manual_key=manual_key,
                            sampling=sampling,
                            orientation=orientation,
                            label_format=label_format,
                            na_text=na_text,
                            nudge_x=nudge_x,
                            nudge_y=nudge_y,
                            nudge_unit=nudge_unit,
                            size_unit=size_unit,
                            bracket_shorten=bracket_shorten,
                            tip_length_unit=tip_length_unit,
                            color_by=color_by,
                            **other_args)
    group_names = dict.fromkeys(data[x_aes]) if ordered_groups is None else ordered_groups
    groups = {v: k for k, v in enumerate(group_names)}
    assert subgroup1 in data, f"subgroup1='{subgroup1}' key isn't in the dataset"
    assert subgroup2 in data, f"subgroup2='{subgroup2}' key isn't in the dataset"
    subgroup_names = dict.fromkeys(list(data[subgroup1]) + list(data[subgroup2])) if ordered_subgroups is None else ordered_subgroups
    subgroups = {v: k for k, v in enumerate(subgroup_names)}
    subgroup_count = len(subgroups.keys())
    dodge_width = dodge_width or .95
    new_data = data.copy()
    new_data["xmin"] = [_dodged_coord(groups[group], subgroups[subgroup], subgroup_count, dodge_width)
                        for (group, subgroup) in zip(data[x_aes], data[subgroup1])]
    new_data["xmax"] = [_dodged_coord(groups[group], subgroups[subgroup], subgroup_count, dodge_width)
                        for (group, subgroup) in zip(data[x_aes], data[subgroup2])]
    del mapping_dict["x"]
    new_mapping = aes(**{**mapping_dict, **{"xmin": "xmin", "xmax": "xmax"}})
    return geom_bracket(mapping=new_mapping,
                        data=new_data,
                        position=position,
                        show_legend=show_legend,
                        manual_key=manual_key,
                        sampling=sampling,
                        orientation=orientation,
                        label_format=label_format,
                        na_text=na_text,
                        nudge_x=nudge_x,
                        nudge_y=nudge_y,
                        nudge_unit=nudge_unit,
                        size_unit=size_unit,
                        bracket_shorten=bracket_shorten,
                        tip_length_unit=tip_length_unit,
                        color_by=color_by,
                        **other_args)