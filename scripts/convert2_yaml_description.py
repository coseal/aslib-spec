'''
Created on Nov 30, 2015

@author: Marius Lindauer
@note: The conversion between old feature group format and new provide/requires format is not optimal and will probably fail in some cases.
'''

import sys
import yaml

def main(fn):

    feature_group_dict = {}
    data = {}
    with open(fn,"r") as fp:
        for line in fp:
            line = line.replace("\n","").strip(" ")
            if line.upper().startswith("SCENARIO_ID"):
                data["scenario_id"] = line.split(":")[1].strip(" ")
            elif line.upper().startswith("PERFORMANCE_MEASURES" ):
                data["performance_measures"] = map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(","))
            elif line.upper().startswith("MAXIMIZE"):
                data["maximize"] = line.split(":")[1].strip(" ").split(",")
            elif line.upper().startswith("PERFORMANCE_TYPE"):
                data["performance_type"] = map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(","))
            elif line.upper().startswith("ALGORITHM_CUTOFF_TIME"):
                data["algorithm_cutoff_time"] = float(line.split(":")[1])
            elif line.upper().startswith("ALGORITHM_CUTOFF_MEMORY"):
                data["algorithm_cutoff_memory"] = float(line.split(":")[1])
            elif line.upper().startswith("FEATURES_CUTOFF_TIME"):
                data["features_cutoff_time"] = float(line.split(":")[1])
            elif line.upper().startswith("FEATURES_CUTOFF_MEMORY"):
                data["features_cutoff_memory"] = float(line.split(":")[1])
            elif line.upper().startswith("FEATURES_DETERMINISTIC"):
                data["features_deterministic"] = map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(","))
            elif line.upper().startswith("FEATURES_STOCHASTIC"):
                data["features_stochastic"] = map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(","))
            elif line.upper().startswith("ALGORITHMS_DETERMINISTIC"):
                data["algorithms_deterministic"] = filter(lambda x: True if x else False, map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(",")))
            elif line.upper().startswith("ALGORITHMS_STOCHASTIC"):
                data["algorithms_stochastic"] = filter(lambda x: True if x else False, map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(",")))
            elif line.upper().startswith("FEATURE_STEP"):
                group_name = line.split(":")[0][12:].strip(" ")
                features = map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(","))
                feature_group_dict[group_name] = features
            elif line.startswith("default_step"):
                data["default_steps"] = filter(lambda x: True if x else False, map(lambda x: x.strip(" "), line.split(":")[1].strip(" ").split(",")))

    # feature group -> 
        # requires -> [] group names
        # provides -> feature names
    
    data["feature_steps"] = {}
    for fgroup in feature_group_dict.keys():
        data["feature_steps"][fgroup] = {"requires": [], "provides": []}
    
    #TODO: this is only a heuristic
    for fgroup, feats in feature_group_dict.items():
        provides = set(feats)
        for fgroup_other, feats_other in feature_group_dict.items():
            if fgroup_other != fgroup:
                if set(feats).difference(feats_other):
                    provides = provides.difference(feats_other)
                elif set(feats_other).difference(feats):
                    data["feature_steps"][fgroup]["requires"].append(fgroup_other)
        data["feature_steps"][fgroup]["provides"] = list(provides)

    yaml.dump(data, sys.stdout, default_flow_style=False)

if __name__ == '__main__':
    main(sys.argv[1])