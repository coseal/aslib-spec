# -*- coding: utf-8 -*-
"""scatterable.py
"""

import bark_to_byte as bb
import altair as alt
import pandas as pd

def make_graph(data_source, x_axis, y_axis, point_marker = 'circle'):
  
  if(point_marker == 'circle'):
      new_graph = alt.Chart(data_source).mark_circle(size=60).encode(
          x = x_axis,
          y = y_axis
      )
      
  elif(point_marker == 'rect'):
      new_graph = alt.Chart(data_source).mark_rect().encode(
          x = x_axis,
          y = y_axis
      )
      
  elif(point_marker == 'bar'):
      new_graph = alt.Chart(data_source).mark_bar().encode(
          x = x_axis,
          y = y_axis
      )
    
  else:
      new_graph = alt.Chart(data_source).mark_point().encode(
          x = x_axis,
          y = y_axis
      )
  
  return new_graph

def make_dropdown(data_source, column, name_prefix):
  opts = list(data_source[column].unique())
  dropdown = alt.binding_select(options = opts)
  select = alt.selection_single(fields = [column],
                                bind = dropdown,
                                name = name_prefix
                               )
  
  return select

def make_selection(array_of_fields, is_multi = False):
  if (is_multi):
    selection = alt.selection_multi(fields = array_of_fields)
  else:
    selection = alt.selection_single(fields = array_of_fields)
    
  return selection

def make_color_scheme(data_source, column, colors, data_type_encoding = 'N'):
  scheme_domain = list(data_source[column].unique())
  scheme_range = colors
  
  scheme_scale = alt.Scale(domain = scheme_domain,
                    range = scheme_range)
  
  #altair needs to know if data is nominal, quantitative, ordinal, or temporal
  if(data_type_encoding == 'N' or data_type_encoding == 'Q' or
      data_type_encoding == 'O' or data_type_encoding == 'T'):
    column_typed = column + ':' + data_type_encoding
  else:
    column_typed = column + ':N'
  
  color_scheme = alt.Color(column_typed,
                           legend = None,
                           scale = scheme_scale)
  
  return color_scheme

def make_color_condition(selector, color_true, color_false = alt.value('darkgray')):
  condition = alt.condition(selector,
                            color_true,
                            color_false)
  
  return condition

def apply_selection_color(chart, selector, color_condition):
  colored_chart = chart.add_selection(
        selector
      ).encode(
        color = color_condition
      )
  
  return colored_chart

def create_comparative_scatter(data_source, key, x_category, y_category, 
                               x_data, y_data, x_filter, y_filter,
                               data_color):
  
  #filter data on x and y axis
  data_legend_base = make_graph(data_source, x_category, y_category, 'rect')
  data_legend_selector = make_selection([x_category, y_category])
  data_legend_colors = make_color_scheme(data_source, y_category, data_color)
  data_legend_update = make_color_condition(data_legend_selector, 
                                            data_legend_colors)
  data_legend = apply_selection_color(data_legend_base, data_legend_selector,
                                      data_legend_update)
  
  #filter data based on attribute
  filter_legend_base = make_graph(data_source, x_filter, y_filter, 'rect')
  filter_legend_selector = make_selection([x_filter, y_filter], True)
  filter_legend_colors = make_color_scheme(data_source, y_filter, data_color)
  filter_legend_update = make_color_condition(filter_legend_selector,
                                              filter_legend_colors)
  filter_legend = apply_selection_color(filter_legend_base, 
                                        filter_legend_selector, 
                                        filter_legend_update)
  
  #set up scatter plot to listen to both legends
  scatter_base = make_graph(data_source, x_data, y_data)
  scatter_tooltip = scatter_base.encode(
                                tooltip = [key, x_category, x_data, x_filter,
                                           y_category, y_data, y_filter]
                            )
  scatter_plot = scatter_tooltip.transform_filter(data_legend_selector
                            ).transform_filter(filter_legend_selector
                            ).interactive()
  
  
  comparative_chart = (data_legend & filter_legend) | scatter_plot
  
  return comparative_chart

