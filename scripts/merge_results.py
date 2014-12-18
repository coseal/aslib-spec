#!/bin/python 

'''
    collects the performance data from several csv data;
    returns a merged csv file (one column per selector)
    and performance data
    @author: Marius Lindauer
'''

import sys
import argparse
import os
import json
import csv

import arff
import logging

from misc.printer import Printer
from coseal_reader import CosealReader
from stat_tests.PermutationTester import PermutationTester

class CSVEvalution(object):
    
    def __init__(self):
        '''
            Constructor
        '''
        

        
    def main(self):
        '''
            main method of Checker
        '''
        parser = argparse.ArgumentParser(usage="python merge_results.py --dir <Scenario> <selector_1>.csv <selector_2>.csv ...")
        parser.add_argument("--dir",dest="dir_", required=True, help="directory path with ASlib Scenario")
        parser.add_argument("--verbose", choices=["INFO", "DEBUG"], default="INFO")
        
        args_, misc = parser.parse_known_args(sys.argv[1:])
        
        logging.basicConfig(format="[%(levelname)s]: %(message)s", level=args_.verbose)
        
        # dummy parameter
        args_.feat_time = -1
        args_.feature_steps = None
        
        # read coseal data
        reader = CosealReader()
        instance_dict, metainfo, algo_dict = reader.parse_coseal(coseal_dir = args_.dir_, args_=args_)
        unsolved_instances = self.get_unsolved_instances(instance_dict)

        sel_perf_dict = {}

        for csv in misc:
            selector = os.path.basename(csv).split(".")[0]
            if not os.path.isfile(csv):
                logging.error("Not found: %s" %(csv))
                sys.exit(1)
        
            inst_time_dict = self.read_csv(csv, metainfo.algorithm_cutoff_time)
            complete_dict = self.cleanup_dict(instance_dict.keys(), unsolved_instances, inst_time_dict, metainfo.algorithm_cutoff_time, selector)
            par10 = self.get_par10_stats(selector, complete_dict)
            sel_perf_dict[selector] = (complete_dict, par10)
            
        sorted_sels = sorted(sel_perf_dict.items(), key=lambda x: x[1][1])
        logging.debug("Ranking:")
        for sel, perfs in sorted_sels:
            logging.debug("%s: %.1f" %(sel, perfs[1]))
        
        #perform statistical permutation test against the best selector
        logging.info("Statistical Test")
        for sel, perfs in sorted_sels[1:]:
            tester = PermutationTester()
            rejected, switched, pValue = tester.doTest(sorted_sels[0][1][0], perfs[0])
            if rejected == True:
                logging.info("%s is statistically better than %s (p-value %.2f)" %(sorted_sels[0][0], sel, pValue))
            else:
                logging.info("%s is not statistically better than %s (p-value %.2f)" %(sorted_sels[0][0], sel, pValue))
        
        
    def read_csv(self, csv_file, cutoff):
        '''    read csv file with performance
                first col: instance name
                second col: runtime performance
               Returns: dictionary: inst_name -> PAR10 score
        '''
        instance_time_dict = {}
        with open(csv_file) as fp:
            csv_reader = csv.reader(fp)
            for row in csv_reader:
                inst = row[0].strip(" ")
                try:
                    time = float(row[1])
                    if time >= cutoff:
                        time = cutoff*10
                except:
                    continue
                instance_time_dict[inst] = time
        return instance_time_dict
    
    def get_unsolved_instances(self, inst_dict):
        '''
            checks the runstatus of each instance and returns the number of instances that was not solved by any solver
        '''
        unsolved_instances = []
        for name, inst_ in inst_dict.iteritems():
            if "ok" not in inst_._status.values():
                unsolved_instances.append(name)
                
        logging.debug("Unsolved Instances: %d" %(len(unsolved_instances)))
        return unsolved_instances
    
    def get_par10_stats(self, name, inst_time_dict):
        n = len(inst_time_dict)
        par10 = sum(inst_time_dict.itervalues()) / n
        logging.info("PAR10 (%s): %.1f" %(name, par10))
        return par10
        
    def cleanup_dict(self, insts, unsolved_inst, sel_dict, cutoff, name):
        '''
            extends the dictionaries of each selector by the instances with a timeout that are not listed
        '''
        exist_inst = set(sel_dict.keys())
        unsolved_inst = set(unsolved_inst)
        solvable = set(insts).difference(unsolved_inst)
        
        adding_inst = solvable.difference(exist_inst)
        removing_inst = unsolved_inst.intersection(exist_inst)
        
        if adding_inst:
            logging.warn("For some instances (%d), %s has not reported results. We assume timeouts." %(len(adding_inst), name))
            for i in adding_inst:
                sel_dict[i] = cutoff*10
        if removing_inst:
            logging.warn("We remove instances (%d) that were not solved by any solver for %s." %(len(removing_inst), name))
            for i in removing_inst:
                del sel_dict[i]
        
        return sel_dict
        
        
if __name__ == '__main__':
    
    eva = CSVEvalution()
    eva.main()