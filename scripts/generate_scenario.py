"""
generate_scenario.py -- reads performance data and features from a csv files and generates a simple ASlib scenario

Assumption: features with -512 (missing value) indicate a timeout during feature computation

@author: Marius Lindauer

"""

import os
import sys
import argparse
import arff
import yaml
import copy

def generate_scenario(runtime_fn, features_fn, cutoff):
    """ generates an ASlib scenario"""
    
    description = {"scenario_id": "UNKNOWN",
                   "performance_measures": ["runtime"],
                   "maximize": ["false"],
                   "performance_type": ["runtime"], 
                   "algorithm_cutoff_time": cutoff,
                   "algorithm_cutoff_memory": "?",
                   "features_cutoff_time": "?",
                   "features_cutoff_memory": "?",
                   "algorithms_deterministic": "?", #TODO
                   "algorithms_stochastic": "",
                   "features_deterministic": "?", #TODO
                   "features_stochastic": "",
                   "number_of_feature_steps": 1,
                   "feature_steps":{"ALL":{"provides":"?"}}, #TODO
                   "default_steps": ["ALL"]}

    algos = []
    with open(runtime_fn, "r") as fp:
        algos = fp.readline().replace("\n","").split(",")[1:]
        algos = map(lambda x: x.strip("'").replace(" ","_"), algos)
        description["algorithms_deterministic"] = algos

        attributes = [ ["instance_id", "STRING"],
                      ["repetition", "NUMERIC"],
                      ["algorithm", "STRING"],
                      ["runtime", "NUMERIC"],
                      ["runstatus", ["ok" , "timeout" , "memout" , "not_applicable" , "crash" , "other"]]
                      ]

        data = []
        for line in fp:
            line = line.replace("\n","").split(",")
            inst = line[0]
            for algo, perf in zip(algos, line[1:]):
                status = "ok" if float(perf) < cutoff else "timeout"
                data.append([inst, "1", algo, perf, status])
            
    run_data = {"attributes": attributes,
                "data": data,
                "relation" : "ALGORITHM_RUNS"
                }
    with open("algorithm_runs.arff", "w") as fp:
        arff.dump(run_data, fp)
        
        
    instances = []
    status = {}
    with open(features_fn, "r") as fp:
        feats = fp.readline().replace("\n", "").split(",")[1:]
        description["features_deterministic"] = copy.deepcopy(feats)
        description["feature_steps"]["ALL"]["provides"] = feats
        
        attributes = [ ["instance_id", "STRING"],
                      ["repetition", "NUMERIC"]]
        data = []
        
        for f in feats:
            attributes.append([f, "NUMERIC"])
            
        for line in fp:
            line = line.replace("\n","").split(",")
            inst = line[0]
            feats = line[1:]
            if sum(map(float, feats)) == -512*len(feats):
                status[inst] = "timeout"
                feats = ["?"]*len(feats)
            else:
                status[inst] = "ok"
            d = [inst,1]
            d.extend(feats)
            data.append(d)
            
    fv_data = {"attributes": attributes,
                "data": data,
                "relation" : "FEATURES"
                }
    with open("feature_values.arff", "w") as fp:
        arff.dump(fv_data, fp)
        
    fs_data = [[inst, "1", stat] for inst,stat in status.iteritems()]
    fs_attributes = [
                     ["instance_id", "STRING"],
                     ["repetition", "NUMERIC"],
                     ["ALL", ["ok" , "timeout" , "memout" , "not_applicable" , "crash" , "other"]]
                     ]
    
    fs_data = {"attributes": fs_attributes,
                "data": fs_data,
                "relation" : "FEATURES_RUNSTATUS"
                }
    
    with open("feature_runstatus.arff", "w") as fp:
        arff.dump(fs_data, fp)
    
    with open("description.txt", "w") as fp:
        yaml.dump(description, fp, default_flow_style=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--runtime", required=True, help="csv file with runtimes (rows instances, cols algorithms)")
    parser.add_argument("--features", required=True, help="csv file with instance features (rows instances, cols features)")
    parser.add_argument("--cutoff", required=True, type=float, help="runtime cutoff")
    
    args_ = parser.parse_args()
    
    generate_scenario(args_.runtime, args_.features, args_.cutoff)
    