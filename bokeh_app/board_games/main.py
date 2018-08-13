from os.path import dirname, join

import numpy as np
import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div, HoverTool
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc

bgg = pd.read_csv(join(dirname(__file__),"bgg_db_2018_01.csv"))

bgg["color"] = np.where(bgg["rank"] <= 100, "orange", "purple")
bgg["alpha"] = np.where(bgg["rank"] <= 100, 0.9, 0.25)

axis_map = {
    "Average Rating": "avg_rating",
    "Number of Votes": "num_votes",
    "Player Age": "age",
    "Length (minutes)": "avg_time",
    "Game Complexity": "weight",
    "Year": "year",
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
votes = Slider(title="Minimum number of votes", value=100, start=100, end=70000, step=500)
max_year = Slider(title="End Year of game release", start=1940, end=2018, value=2017, step=1)
complexity = Slider(title="Game Complexity", start=0, end=4, value=1.5, step=0.5)
avgtime = Slider(title="Average time for game completion (mins)", start=0, end=6000, value=100, step=1)
playage = Slider(title="Minimum Age of player", start=0, end=21, value=13, step=1)
category = Select(title="Category", value="All",
               options=open(join(dirname(__file__), 'categories.txt')).read().split())
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Average Rating")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Number of Votes")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], geek_rating=[],rank=[], alpha=[]))

TOOLTIPS=[
    ("Name", "@title"),
    ("Year", "@year"),
    ("Geek Rating", "@geek_rating")
]

p = figure(plot_height=450, plot_width=800, title="", toolbar_location=None)
# tooltips=TOOLTIPS)
p.circle(x="x", y="y", source=source, size=9, color="color", line_color=None, fill_alpha="alpha")
hover = HoverTool(tooltips=[("Name", "@title"), ("Year", "@year"),("Geek Rating", "@geek_rating"), ("Rank","@rank")])
p.add_tools(hover)

def select_board_games():
    category_val = category.value
    selected = bgg[
        (bgg.num_votes >= votes.value) &
        (bgg.year <= max_year.value) &
        (bgg.weight >= complexity.value) &
        (bgg.age >= playage.value) &
        (bgg.avg_time >= avgtime.value)
    ]
    if (category_val != "All"):
        selected = selected[selected.category.str.contains(category_val)==True] #check
    return selected


def update():
    df = select_board_games()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d board games selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        title=df["names"],
        year=df["year"],
        geek_rating=df["geek_rating"],
        rank = df["rank"],
        alpha=df["alpha"],
    )

controls = [votes, category,playage, max_year, complexity, avgtime, x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Board Games"
