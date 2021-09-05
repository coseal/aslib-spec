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

def generate_scenario(runtime_fn, features_fn, algo_features_fn, cutoff):
    """ generates an ASlib scenario"""
    
    description = {"scenario_id": "UNKNOWN",
                   "performance_measures": ["runtime"],
                   "maximize": [False],
                   "performance_type": ["runtime"], 
                   "algorithm_cutoff_time": cutoff,
                   "algorithm_cutoff_memory": "?",
                   "features_cutoff_time": "?",
                   "features_cutoff_memory": "?",
                   "algorithms_deterministic": "?", #TODO
                   "algorithms_stochastic": "",
                   "metainfo_algorithms": {},
                   "features_deterministic": "?", #TODO
                   "features_stochastic": "",
                   "feature_steps":{"instance":{"provides":"?"}}} #TODO

    if algo_features_fn: 
        description["algorithm_features_cutoff_time"] = "?"
        description["algorithm_features_cutoff_memory"] = "?"
        description["algorithm_features_deterministic"] = "?"
        description["algorithm_features_stochastic"] = ""
        description["algorithm_feature_steps"] = {"software":{"provides":"?"}}
        description["number_of_feature_steps"] = 2
        description["default_steps"] = ["instance", "software"]
    else: 
        description["number_of_feature_steps"] = 1
        description["default_steps"] = ["instance"]
    
    #default algorithm info
    algo_info = {"configuration": "",
                 "deterministic": "true"}

    algos = []
    with open(runtime_fn, "r") as fp:
        algos = fp.readline().replace("\n","").split(",")[1:]
        algos = map(lambda x: x.strip("'").replace(" ","_"), algos)
        
        algo_infos = {}
        for algo in algos:
            algo_infos[algo] = copy.deepcopy(algo_info)
        description["metainfo_algorithms"] = copy.deepcopy(algo_infos)
        
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
        description["feature_steps"]["instance"]["provides"] = feats
        
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
                     ["instance", ["ok" , "timeout" , "memout" , "not_applicable" , "crash" , "other"]]
                     ]
    
    fs_data = {"attributes": fs_attributes,
                "data": fs_data,
                "relation" : "FEATURES_RUNSTATUS"
                }
    
    with open("feature_runstatus.arff", "w") as fp:
        arff.dump(fs_data, fp)


    if algo_features_fn:
        algorithms = []
        status = {}
        with open(algo_features_fn, "r") as fp:
            feats = fp.readline().replace("\n", "").split(",")[1:]
            description["algorithm_features_deterministic"] = copy.deepcopy(feats)
            description["algorithm_feature_steps"]["software"]["provides"] = feats
            
            attributes = [ ["algorithm", "STRING"],
                          ["repetition", "NUMERIC"]]
            data = []
            
            for f in feats:
                attributes.append([f, "NUMERIC"])
                
            for line in fp:
                line = line.replace("\n","").split(",")
                algo = line[0]
                feats = line[1:]
                if sum(map(float, feats)) == -512*len(feats):
                    status[algo] = "timeout"
                    feats = ["?"]*len(feats)
                else:
                    status[algo] = "ok"
                d = [algo,1]
                d.extend(feats)
                data.append(d)
                
        fv_data = {"attributes": attributes,
                    "data": data,
                    "relation" : "ALGORITHM_FEATURES"
                    }
        with open("algorithm_feature_values.arff", "w") as fp:
            arff.dump(fv_data, fp)
            
        fs_data = [[algo, "1", stat] for algo,stat in status.iteritems()]
        fs_attributes = [
                         ["algorithm", "STRING"],
                         ["repetition", "NUMERIC"],
                         ["software", ["ok" , "timeout" , "memout" , "not_applicable" , "crash" , "other"]]
                         ]
        
        fs_data = {"attributes": fs_attributes,
                    "data": fs_data,
                    "relation" : "ALGORITHM_FEATURES_RUNSTATUS"
                    }
        
        with open("algorithm_feature_runstatus.arff", "w") as fp:
            arff.dump(fs_data, fp)


    with open("description.txt", "w") as fp:
        yaml.dump(description, fp, default_flow_style=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--runtime", required=True, help="csv file with runtimes (rows instances, cols algorithms)")
    parser.add_argument("--features", required=True, help="csv file with instance features (rows instances, cols features)")
    parser.add_argument("--algo_features", required=False, help="csv file with algorithm features (rows algorithms, cols features)")
    parser.add_argument("--cutoff", required=True, type=float, help="runtime cutoff")
    
    args_ = parser.parse_args()
    
    generate_scenario(args_.runtime, args_.features, args_.algo_features, args_.cutoff)
    
