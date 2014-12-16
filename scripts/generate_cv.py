#!/bin/python

'''
    @author: Marius Lindauer
'''

import sys
import os
import arff
import random
import copy

def read_inst(file_):
    fp = open(file_)
    arff_dict = arff.load(fp)
    fp.close()
    insts = []
    for data in arff_dict["data"]:
        inst_name = data[0]
        insts.append(inst_name)
    return insts    

def sample_cv(train_set, folds):
    train_set = copy.copy(train_set)
    inst_fold_dict = {}
    for i in range(0,folds):
        fold = random.sample(train_set, int(len(train_set)*1/(folds-i)))
        sys.stderr.write("Fold: %d Size: %d\n" %(i, len(fold)))
        train_set.difference_update(fold)
        for inst_ in fold:
            inst_fold_dict[inst_] = i+1
    return inst_fold_dict
    
def write_cv(inst_fold_dict):
    print("@relation R_data_frame")

    print("@attribute instance_id string")
    print("@attribute repetition numeric")
    print("@attribute fold numeric")
    
    print("@data")
    for inst_, fold in inst_fold_dict.iteritems():
        print("%s,1,%d" %(inst_, fold))
    
        
FOLDS = 10

if len(sys.argv) != 2:
    print("Usage: python generate_cv.py <aslib_scenario>")
    sys.exit(1)
    
feature_file = os.path.join(sys.argv[1], "feature_values.arff")
if not os.path.isfile(feature_file):
    print("Have not found: %s" %(feature_file))
    
insts = read_inst(feature_file)
inst_fold_dict = sample_cv(set(insts), FOLDS)
write_cv(inst_fold_dict)
