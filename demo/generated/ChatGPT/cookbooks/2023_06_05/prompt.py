def get_prompt(function_name, *, plots_count=[3, 5]):
    plots_count_str = str(plots_count) if type(plots_count) == int else "{0} to {1}".format(*plots_count)

    query = """
I want you to act as a data scientist.

Create a notebook explaining how to use the `{function_name}()` function of the Lets-Plot library.

Use something standard as a dataset, like mpg or iris. The dataset url should look like "https://raw.githubusercontent.com/JetBrains/lets-plot-docs/master/data/%DATASET_NAME%.csv".

Build {plots_count} plots. Use `LetsPlot.setup_html()` before first occurrence of plot. Use a consistent style when choosing colors, sizes and so on.

Here 2 examples of what I expect:
    """.format(
        function_name=function_name,
        plots_count=plots_count_str,
    )

    examples = [
        """
# Plotting Points: geom_point()

The point geometry is used to create scatterplots. The scatterplot is useful for displaying the relationship between two continuous variables, although it can also be used with one continuous and one categorical variable, or two categorical variables.

```python
import numpy as np
from lets_plot import *
```

```python
LetsPlot.setup_html()
```

```python
np.random.seed(10000)
n = 100
data = {
    'x': np.random.rand(n),
    'y': np.random.rand(n),
    'colors': np.random.rand(n),
    'area': (30 * np.random.rand(n))**2,
}
```

## Default Presentation of Point Geometry

```python
p = ggplot(data, aes(x='x', y='y')) 
p + geom_point()
```

## Options

Add aesthetic mappings.

```python
p + geom_point(aes(color='colors', shape='x'), size=5)
```

A "bubblechart".

```python
p + geom_point(aes(size='x'))
```

Set aesthetics to fixed value.

```python
p + geom_point(color='black', size=6, shape=22, fill='red')
```

Varying alpha is useful for large datasets.

```python
np.random.seed(42)
n1, n2 = 1000, 500
big_data = {
    'x': np.append(np.random.normal(0, 1, n1), np.random.normal(3, 1, n2)),
    'y': np.append(np.random.normal(0, 1, n1), np.random.normal(3, 1, n2)),
}
```

```python
ggplot(big_data, aes('x', 'y')) + geom_point(size=3, alpha=0.3)
```

You can create interesting shapes by layering multiple points of different sizes.

```python
p + geom_point(aes(shape='area', color='colors'), size=7) + \\
    geom_point(color='#993404', size=2.5)
```
        """,
        """
# Bar Charts: geom_bar()

geom_bar() displays a bar chart which makes the height of the bar proportional to the number of cases in each group.

geom_bar() uses 'count' stat by default, it counts the number of cases at each x position. Use stat='identity' to leave the data as is.

## Preparation

```python
import pandas as pd

from lets_plot import *
from lets_plot.mapping import *
```

```python
LetsPlot.setup_html()
```

```python
df = pd.read_csv("https://raw.githubusercontent.com/JetBrains/lets-plot-docs/master/data/titanic.csv")
print(df.shape)
df.head()
```

## Default Presentation of Bar Geometry

Here is the simplest example showing the number of passengers in each class.

```python
ggplot(df, aes(x="Pclass")) + geom_bar()
```

## Options

Use the weight aesthetic to count the number of surviving passengers in each class.

```python
ggplot(df, aes(x="Pclass")) + geom_bar(aes(weight="Survived"))
```

Use orientation param to flip the graph.

```python
ggplot(df, aes(y="Pclass")) + geom_bar(orientation='y')
```

Bar charts are automatically stacked when multiple bars are placed at the same location.

```python
ggplot(df, aes(x="Pclass")) + geom_bar(aes(fill=as_discrete("Survived")))
```

Use position='dodge' to draw bars dodged side-to-side.

```python
ggplo

geom_bar() can be used with continuous data. In this case it will show counts at unique locations on the x-axis.

geom_bar() does not uny close values on the x-axis unlike geom_histogram().

```python
data = {
    "x": [3.2] * 2 + [3.85] * 5 + [4.1] * 3
}
```

```python
width, height = 400, 300

g = ggplot(data, aes(x="x"))

bunch = GGBunch()
bunch.add_plot(g + geom_bar() + ggtitle("Bar"), 0, 0, width, height)
bunch.add_plot(g + geom_histogram(binwidth=.5) + ggtitle("Histogram"), width, 0, width, height)
bunch.show()
```

## Identity Stat

Use stat='identity' to display the mean fare for each class as is.

```python
agg_df = df.groupby("Pclass")["Fare"].mean().to_frame("Mean_Fare").reset_index()
agg_df
```

```python
ggplot(agg_df, aes(x="Pclass", y="Mean_Fare")) + geom_bar(stat='identity', tooltips='none')
```

## Demo

```python
ggplot(df, aes(x="Pclass")) + \\
    geom_bar(aes(fill=as_discrete("Survived")), color='black') + \\
    facet_grid(x="Sex") + \\
    scale_x_continuous(breaks=[1, 2, 3]) + \\
    scale_fill_brewer(type='qual', palette='Pastel1') + \\
    xlab("passenger class") + ylab("passengers number") + \\
    ggtitle("Survivors by passenger class") + \\
    theme_classic() + flavor_solarized_light()
```
        """,
    ]

    return "{query}\n\n{examples}".format(
        query=query,
        examples="\n".join(["{0}.\n{1}\n".format(i + 1, example) for i, example in enumerate(examples)])
    )