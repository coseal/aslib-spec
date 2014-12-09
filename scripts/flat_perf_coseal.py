#!/bin/python

'''
    @author: Marius Lindaue
    @contact: lindauer@cs.uni-freiburg.de

    A simple script to convert ASlib format to ISAC and SNNAP format.
    Restrictions:
     * only runtime scenarios are supported
     * only the default feature steps are used
     
    ATTENTION: Writes output files without warnings (maybe overwrites old files)
'''

import sys
import os
import arff
import random
import copy
import logging

def read_description(file_):
    cutoff = None
    steps = {}
    default_steps = []
    with open(file_) as fp:
        for line in fp:
            line = line.strip("\n")
            if line.startswith("feature_step"):
                name, feats = line.lstrip("feature_step").split(":")
                name = name.strip(" ")
                feats = map(lambda x: x.strip(" "), feats.split(","))
                steps[name] = feats
            if line.startswith("default_steps"):
                defs = line.lstrip("default_steps:")
                default_steps = map(lambda x: x.strip(" "), defs.split(","))
            if line.startswith("algorithm_cutoff_time"):
                cutoff = float(line.lstrip("algorithm_cutoff_time:").strip(" "))
                
    logging.debug("Cutoff: %.1f" %(cutoff))
    logging.debug("Steps: %s" %(str(steps)))
    logging.debug("Default Steps: %s" %(",".join(default_steps)))
    
    # find usable features of default steps
    unused_features = set()
    unused_steps = set(steps.keys()).difference(set(default_steps))
    for u_step in unused_steps:
        not_processed_features = steps[u_step]
        unused_features = unused_features.union(set(not_processed_features))
        
    all_features = set()
    for feats in steps.values():
        all_features.update(feats)
        
    used_features = set(all_features).difference(unused_features)
        
    print("Active Features: %s" %(",".join(used_features)))
                
    return cutoff, steps, default_steps, used_features
    

def read_inst(file_, cutoff):
    '''
        EXPECTED HEADER:
        @RELATION ALGORITHM_RUNS_2013-SAT-Competition

        @ATTRIBUTE instance_id STRING
        @ATTRIBUTE repetition NUMERIC
        @ATTRIBUTE algorithm STRING
        @ATTRIBUTE PAR10 NUMERIC
        @ATTRIBUTE Number_of_satisfied_clauses NUMERIC
        @ATTRIBUTE runstatus {ok, timeout, memout, not_applicable, crash, other}
    '''
    
    fp = open(file_)
    arff_dict = arff.load(fp)
    fp.close()
    
    solvers = set()
    instance_dict = {}
    for data in arff_dict["data"]:
        inst = data[0]
        algo = data[2]
        solvers.add(algo)
        if data[3] is None:
            time = cutoff
        else:
            time = float(data[3])
        status = data[4]
        if status != "ok":
            time = cutoff
        instance_dict[inst] = instance_dict.get(inst,{})
        instance_dict[inst][algo] = time
    return instance_dict, solvers

def read_costs(file_, default_steps, instance_dict, inst_status, cutoff, add_costs=True):
    '''
        Expected header:
        @RELATION FEATURE_COSTS_2013-SAT-Competition

        @ATTRIBUTE instance_id STRING
        @ATTRIBUTE repetition NUMERIC
        @ATTRIBUTE preprocessing NUMERIC
        @ATTRIBUTE local_search_probing NUMERIC
    '''
    
    fp = open(file_)
    arff_dict = arff.load(fp)
    fp.close()
    
    active_indx = []
    indx = 0
    for step,_ in arff_dict["attributes"][2:]:
        if step in default_steps:
            active_indx.append(indx)
        indx += 1    
    
    for data in arff_dict["data"]:
        inst = data[0]
        costs = data[2:]
        costs = [costs[idx] for idx in active_indx] #use only costs of active steps
        
        costs = map(lambda x: 0 if x is None else float(x), costs)
        costs = sum(costs)
        for solver, time in instance_dict[inst].items():
            if not add_costs: # optimistic performance estimation
                costs = 0
            if inst_status[inst]: # presolved
                time = costs
            elif time + costs >= cutoff:
                time = cutoff + 100
            else:
                time = time + costs
            instance_dict[inst][solver] = time
    return instance_dict

def read_status(file_, default_steps):
    '''
        Expected header:
        @RELATION FEATURE_RUNSTATUS_2013 - SAT - Competition
        @ATTRIBUTE instance_id STRING
        @ATTRIBUTE repetition NUMERIC
        @ATTRIBUTE preprocessing { ok , timeout , memout , presolved , crash , other }
        @ATTRIBUTE local_search_probing { ok , timeout , memout , presolved , crash , other }
    '''
    fp = open(file_)
    arff_dict = arff.load(fp)
    fp.close()
    
    active_indx = []
    indx = 0
    for step,_ in arff_dict["attributes"][2:]:
        if step in default_steps:
            active_indx.append(indx)
        indx += 1    

    inst_status = {}
    for data in arff_dict["data"]:
        inst = data[0]
        stati = data[2:]
        presolved = False
        for indx in active_indx: 
            if "presolved" == stati[indx]:
                presolved = True
                break
        inst_status[inst] = presolved
    return inst_status

def write_cv_isac(instance_dict, solvers):
    solvers = list(solvers)
    fp = open("perf.data", "w")
    for inst, perfs in instance_dict.items():
        perfs = [perfs[solver] for solver in solvers]
        fp.write("%s\t%s\n" %(inst, "\t".join(map(str,perfs))))
    fp.close()
        
def write_cv_snnap(instance_dict, solvers):
    solvers = list(solvers)
    fp = open("perf.data", "w")
    fp.write("\"\",%s\n" %(",".join(solvers)))
    for inst, perfs in instance_dict.items():
        perfs = [perfs[solver] for solver in solvers]
        fp.write("%s,%s\n" %(inst, ",".join(map(str,perfs))))        
    fp.close()   
     
def rewrite_feature_values(feature_file, active_features, mode="SNAPP"):
    fp = open(feature_file)
    arff_dict = arff.load(fp)
    fp.close()
    
    features = []
    active_indx = []
    idx = 0
    for fname in arff_dict["attributes"][2:]:
        if fname[0] in active_features:
            features.append(fname[0])
            active_indx.append(idx)
        idx += 1
        
    logging.debug("#Features: %d" %(len(features)))

    fp = open("feature.data", "w")
    if mode == "SNAPP":
        fp.write("\"\",%s\n" %(",".join(features)))
    
    for data in arff_dict["data"]:
        inst = data[0]
        features = data[2:]
        features = [features[idx] for idx in active_indx]
        features = map(lambda x: -512 if x is None else x, features)
        if mode == "SNAPP":
            fp.write("%s,%s\n"%(inst, ",".join(map(str,features))))
        elif mode == "ISAC":
            fp.write("%s\t%s\n"%(inst, "\t".join(map(str,features))))    
        
    fp.close()
        
        
'''Usage: python generate_cv_coseal.py <coseal-dir>'''
        
logging.basicConfig(level=logging.DEBUG)        
        
OUTPUT = "ISAC"
#OUTPUT = "SNNAP"
ADD_COSTS = True # False: optimistic performance estimate
        
algo_runs = os.path.join(sys.argv[1], "algorithm_runs.arff")
feature_costs = os.path.join(sys.argv[1], "feature_costs.arff")
feature_status = os.path.join(sys.argv[1], "feature_runstatus.arff")
feature_values = os.path.join(sys.argv[1], "feature_values.arff")
description = os.path.join(sys.argv[1], "description.txt")

cutoff, steps, default_steps, used_features = read_description(description)

if not os.path.isfile(algo_runs):
    sys.stderr.write("ERROR: not found: %s\n" %(algo_runs))
    sys.exit(1)
    
if os.path.isfile(feature_costs) and os.path.isfile(feature_status):
    sys.stderr.write("Respect Costs and Status of Features\n")
    inst_dict, solvers = read_inst(algo_runs, cutoff)
    inst_status = read_status(feature_status, default_steps) 
    inst_dict = read_costs(feature_costs, default_steps, inst_dict, inst_status, cutoff, add_costs=ADD_COSTS)
else:        
    inst_dict, solvers = read_inst(algo_runs, cutoff)

#print("Insts: %d" %(len(insts)))

if OUTPUT == "ISAC":
    write_cv_isac(inst_dict, solvers)
elif OUTPUT == "SNNAP":
    write_cv_snnap(inst_dict, solvers)

rewrite_feature_values(feature_values, used_features, OUTPUT)
