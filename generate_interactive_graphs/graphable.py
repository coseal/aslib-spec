# -*- coding: utf-8 -*-
""" graphable.py
The script that actually generates a graph. Must include the methods: 
* create_graph()

If the graph can be generated, returns an Altair scatter plot.<br>
If not, prints error statement and returns an empty variable.<br> 
If the graphed performance measure isn't the one you expected, you can explicitly specify it by passing in the (exact) measure (not performance type) as a string.
<br><br>
Currently, it creates a graph comparing the first two algorithms' runtimes. It also displays a legend of algorithms and a legend of runstatuses.

#Imports
"""

# pip install liac_arff

import altair as alt
import pandas as pd
import bark_to_byte as bb
alt.data_transformers.disable_max_rows()

"""#Helpers

Convert to dataframe<br>
TODO: move bark_to_byte code here instead of importing module
"""

def convert_to_dataframe(file_name):
  df = bb.arff_to_dataframe(file_name)
  return df

"""Check if performance measure exists"""

def get_performance_measure(df):

  possible_measures = ['runtime', 'solution_quality', 'PAR10', 'obj']

  columns = list(df.columns)

  for pm in possible_measures:
    if (pm in columns):
      return pm

  return None

"""Check if solution measure is present in source columns."""

# check if scenario uses desired performance measure
# therefore also checks whether input is, in fact, a scenario

def should_run(df, sltn_msr):
  if (sltn_msr):
    return True
  
  return False

"""Formats data so graphing methods can manipulate it, using join technique."""

# formatting for JOIN technique
# set up so each instance only has one row, with twice the original columns;
#   each is of the format "column_name" + "_x" and "column_name" + "_y"
def format_data_join(df):
  # ensure keys are correct
  df = df.set_index('instance_id')

  # join set with itself, add "_x" suffix on left, "_y" suffix on right
  df_joined = df.join(df, lsuffix='_x', rsuffix='_y')

  # cleanup, re-flattens index
  df_joined.reset_index(inplace=True)

  return df_joined

"""Create scatter plot from joined data"""

def create_scatter_join(df, performance_measure, mkr_size = 60):
  x_msr = performance_measure + '_x'
  y_msr = performance_measure + '_y'

  new_sctr = alt.Chart(df).mark_circle(size=mkr_size).encode(
      x = x_msr,
      y = y_msr,
      tooltip = ['instance_id', 'algorithm_x', 'algorithm_y',
                 x_msr, y_msr, 'runstatus_x', 'runstatus_y']
  )

  new_sctr = new_sctr.interactive()

  return new_sctr

"""Create legend"""

def create_legend(df, x_axis, y_axis):

  new_lgd = alt.Chart(df).mark_rect().encode(
      x = x_axis,
      y = y_axis
  )

  return new_lgd

"""Define color change behavior when selector updates"""

def create_color_condition(selector, color_true = alt.value('steelblue'), 
                           color_false = alt.value('darkgray')):

  condition = alt.condition(selector, color_true, color_false)

  return condition

"""#Main Method

TODO: adjust custom performance measure error handling
"""

def create_graph(arff_file_name, sltn_measure = ''):
  source = convert_to_dataframe(arff_file_name)

  # check if solution measure is present in source columns, otherwise don't bother
  if (sltn_measure == ''):
    sltn_measure = get_performance_measure(source)
  is_correct_sltn_measure = should_run(source, sltn_measure)

  if(is_correct_sltn_measure):
    # format data
    dataframe = format_data_join(source)

    # create plots
    scatter = create_scatter_join(dataframe, sltn_measure)
    alg_legend = create_legend(dataframe, 'algorithm_x', 'algorithm_y')
    stat_legend = create_legend(dataframe, 'runstatus_x', 'runstatus_y')

    # add interactivity
    alg_selector = alt.selection_single(fields = ['algorithm_x', 'algorithm_y'])
    stat_selector = alt.selection_multi(fields = ['runstatus_x', 'runstatus_y'])

    alg_legend = alg_legend.add_selection(alg_selector)
    stat_legend = stat_legend.add_selection(stat_selector)

    alg_colors = create_color_condition(alg_selector)
    stat_colors = create_color_condition(stat_selector)

    alg_legend = alg_legend.encode(color = alg_colors)
    stat_legend = stat_legend.encode(color = stat_colors)

    scatter = scatter.transform_filter(alg_selector)
    scatter = scatter.transform_filter(stat_selector)

    # concat finished plots
    graph = (alg_legend & stat_legend) | scatter


  else:
    print(arff_file_name + ": Cannot create graph.")
    graph = None
  
  return graph


