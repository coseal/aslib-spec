# -*- coding: utf-8 -*-
"""bark_to_byte.py
Bark to Byte

<h2>Goal: Move .arff data into a dataframe</h2>

Functionality: <br>
*  Given an arff file, remove the attribute data types and create a pandas DataFrame
*  Format comparison for "where_equals" data filtering


Future work:


*   Use multi-indexing to preserve the data types
*   Use np array instead of list, for speed / optimization

Notes: 

*  Variable declarations and assignments may be out of order, because I moved the cells around

<h4>Imports</h4>

Commented so it works as an imported module. If running this alone, check that liac_arff has been installed.
"""

#pip install liac_arff

import arff
import pandas as pd
import numpy as np

"""<h4>Helpers</h4>

These must be defined above the primary method in order to cooperate, apparently :D

Get arff data: returns a dictionary<br>

---<br>


Format:

*   'attributes' : [('Name Element0', 'TYPE'), ('Name' Element1, 'TYPE')]
*   'data': [<br>
[Entry0 Element0, Entry0 Element1], <br>
[Entry1 Element0, Entry1 Element1],
<br>]
"""

def open_file(name):
  file = open(name);
  loaded = arff.load(file);
  
  return loaded;


"""Given a list of lists, extracts the first element of each. (Specifically, used to get name of each attribute without extra data so we can use it as a column header)"""

def get_first(tuple_list):
  
  first_only = [];
  
  for el in tuple_list:
    first = el[0];
    first_only.append(first);
    
  return first_only;

"""Given data and a list of column headers, constructs a dataframe."""

def to_dataframe(data, cols):
  dataframe = pd.DataFrame(data, columns = cols);
  return dataframe;

"""<h4>Primary Methods</h4>

Given an .arff file, return a data frame
"""

def arff_to_dataframe(filename):
  loaded = open_file(filename);
  data = loaded['data'];
  atts = loaded['attributes'];
  col_headers = get_first(atts);
  
  frame = to_dataframe(data, col_headers);
  
  return frame;


"""Given a dataframe, column name, and something to compare to, return the relevant entries"""

def where_equals(dataframe, column, is_equal_to):
  source_column = dataframe[column]
  where_clause = source_column == is_equal_to
  
  matching_data = dataframe.loc[where_clause]
  
  return (matching_data);


