#!/bin/python

'''
Created on Dec 08, 2015

@author: Marius Lindauer

'''

import sys
import argparse
import os
import json
import csv

import arff

from misc.printer import Printer
from coseal_reader import CosealReader

class ZillaEva(object):
    
    def __init__(self):
        '''
            Constructor
        '''
        pass

        
    def main(self):
        '''
            main method of Checker
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument("--dir",dest="dir_", required=True, help="directory path with input files")
        parser.add_argument("--csv",dest="csv_", required=True, help="csv in zilla \"manual\" style")
        
        args_ = parser.parse_args(sys.argv[1:])
        
        # dummy parameter
        args_.feat_time = -1
        args_.feature_steps = None
        
        # read coseal data
        reader = CosealReader()
        instance_dict, metainfo, algo_dict = reader.parse_coseal(coseal_dir = args_.dir_, args_=args_)
        args_.feature_steps = [metainfo.feature_steps[0]] # consider only the first default step as cheap feature step
        reader = CosealReader()
        instance_dict, metainfo, algo_dict = reader.parse_coseal(coseal_dir = args_.dir_, args_=args_) # parse a second time to fix feature costs

        inst_time_dict = self.read_zilla_csv(args_.csv_, metainfo.algorithm_cutoff_time)
        self.get_stats(inst_time_dict, instance_dict, metainfo.algorithm_cutoff_time)
        
    def read_zilla_csv(self, csv_file, cutoff):
        instance_time_dict = {}
        with open(csv_file) as fp:
            csv_reader = csv.reader(fp)
            for row in csv_reader:
                inst = row[0]
                try:
                    time = float(row[1])
                    if time >= cutoff:
                        time = cutoff*10
                except:
                    continue
                instance_time_dict[inst] = time
        return instance_time_dict
    
    def get_stats(self, inst_time_dict, instance_dict, cutoff):
        par10 = sum(inst_time_dict.itervalues()) /len(inst_time_dict)
        print("PAR10 (w/o costs): %.1f" %(par10))
        
        for inst, time in inst_time_dict.items():
            f_time = instance_dict[inst]._feature_cost_total
            sum_time = f_time + time
            if sum_time >= cutoff:
                sum_time = cutoff*10
            inst_time_dict[inst] = sum_time
            
        par10 = sum(inst_time_dict.itervalues()) /len(inst_time_dict)
        print("PAR10 (w costs): %.1f" %(par10))
                
        
if __name__ == '__main__':
    
    zilla_eva = ZillaEva()
    zilla_eva.main()
