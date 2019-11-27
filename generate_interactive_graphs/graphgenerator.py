# -*- coding: utf-8 -*-
"""graphgenerator.py
This module searches for uploaded .arff files, uses the graphable module to create the interactive graph for each, then triggers a browser download for each .html file generated.


NOTES: <br>
* .arff files must have unique names, or the graphs will overwrite each other.
* If the graph does not have the expected performance measure, specify it explicitly. Modify <br><br>
<code> graph = gr.create_graph(src) </code> <br><br>
to include your desired performance measure, for example, runtime.<br><br>
<code> graph = gr.create_graph(src, "runtime") </code>


Uses: 
* graphable.py
* bark_to_byte.py

* Reset all runtimes (so colab doesn't get confused between the new and old copies of the module)
* Upload new graphable module, as well as other file dependencies
* Re-compile all imports and methods

#Imports
"""

# so we can parse the .arff file
import os
import bark_to_byte as bb
import graphable as gr
import argparse 

"""#Main Code Blocks
* Get uploaded .arff files
* Create a graph for each 
* Trigger browser download of each .html file

Iterate through files in current working directory; extract .arff files
"""

def search_for_ext(path, ext):
  files_in_dir = os.listdir(path)
  type_files = []
  ext_length = len(ext)

  for fn in files_in_dir:
    name_length = len(fn)
    ext_pos = name_length - ext_length
    type_pos = fn.find(ext, ext_pos)
    is_type = False
  
    if (type_pos >= 0):
      is_type = True

    if (is_type):
      type_files.append(os.path.join(path, fn))
    
  return type_files

"""Iterate through .arff files; create a graph for each, and save it as .html"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--path", required=True, help="path with arff files")
    parser.add_argument("--save", required=True, help="path to save generated files")
    args_ = parser.parse_args()

    # get the scenarios to graph
    arff_files = search_for_ext(args_.path, ".arff")
    data_sources = arff_files

    for src in data_sources:
      print("generating: " + src)
      # make a graph, setup to save
      graph = gr.create_graph(src)
      name = src.replace(".arff", "")

      # if it worked, save the graph
      try:
        name = os.path.basename(name)
        name = os.path.join(args_.save, name)
        graph.save(name + ".html")
      except:
        pass
