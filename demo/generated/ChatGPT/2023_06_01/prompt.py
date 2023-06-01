import pandas as pd

def col_info(df, col):
    name = col
    s = df[col]
    dtype = s.dtype
    not_nn_count = s.notnull().count()
    unique_count = s.unique().size
    return '"{0}" ({1}): {2} non-null values, {3} unique values;'.format(name, dtype, not_nn_count, unique_count)

def get_prompt(*, url=None, read_csv=None, name=None, plots_count=[3, 5], target=[]):
    if url is not None:
        original_df = pd.read_csv(url)
    elif read_csv is not None:
        original_df = read_csv()
    else:
        raise Exception("Should be specified one of the following parameters: url, read_csv")
    df = original_df.loc[:, (original_df != original_df.iloc[0]).any()]

    url_str = "" if url is None else "\n\nThe data can be found at {0}".format(url)

    dataset_name = '' if name is None else ' "{0}"'.format(name)

    dataset_shape = df.shape

    column_descriptions = '\n'.join([col_info(df, col) for col in df.columns])

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

I have a dataset{name} of shape {shape} with the following columns:
{columns}{url}

Write code for data visualization and exploration. Build {plots_count} plots on the dataset. Organize the code so that it is suitable for Jupiter notebook. {target}

For visualization use the Lets-Plot library. Use `LetsPlot.setup_html()` before first occurrence of plot. Try not to use parameters that depends on data (such as 'binwidth'). Use a consistent style when choosing colors, sizes and so on. Set colors only in hex format. Each cell with plot must end with an implicit call, without using `show()`, `print()`, etc. If you are trying to plot some geospatial data, don't forget to use the `coord_map()` function. Use only those functions that are presented on the API page of the library.

And do not try to replace the Lets-Plot by another one visualization library.
    """.format(
        name=dataset_name,
        url=url_str,
        shape=dataset_shape,
        columns=column_descriptions,
        plots_count=plots_count_str,
        target=target_description
    )