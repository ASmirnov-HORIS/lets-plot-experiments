def get_prompt(df, *, name=None, plots_count=[3, 5], target=[]):
    dataset_name = '' if name is None else ' "{0}"'.format(name)
    column_descriptions = '\n'.join([
        '"{0}" ({1})'.format(col, dtype)
        for col, dtype in df.dtypes.items()
    ])
    target_cols = [target] if type(target) == str else target
    target_description = 'Pay special attention to the columns that seem most interesting to you.' \
    if len(target_cols) == 0 else """
I am particularly interested in the {columns} column{ending}.
    """.format(
        columns=', '.join(['"{0}"'.format(col) for col in target_cols]),
        ending=('s' if len(target_cols) > 1 else '')
    ).strip()
    plots_count_str = str(plots_count) if type(plots_count) == int else "{0} to {1}".format(*plots_count)
    return """
I want you to act as a data scientist.

I have a dataset{name} with the following columns:
{columns}

Write code for data visualization and exploration. Build {plots_count} plots on the dataset. Organize the code so that it is suitable for Jupiter notebook. {target}

For visualization use the Lets-Plot library. Use `LetsPlot.setup_html()` before first occurrence of plot. Try not to use parameters that depends on data (such as 'binwidth'). Use a consistent style when choosing colors, sizes and so on. If you are trying to plot some geospatial data, don't forget to use the coord_map() function.
    """.format(name=dataset_name, columns=column_descriptions, plots_count=plots_count_str, target=target_description)