#!/usr/bin/env python3
# python >= 3.7
 
from lattice import *
from partt import *
from rm_solver import RMSolver
from parser import *
from result import *
import time
import globals
import sys

from typing import List
import logging
import unittest

class PartitionDerivationSolver:
    def __init__(self, partt=SequentialPartition(), lat=TwoPointLattice(), timeout=3):
        assert isinstance(lat, Lattice)
        assert isinstance(partt, PartitionContext)
        self.lattice = lat
        self.rm = RMSolver(lat)
        self.partt = partt
        self.solution = {}
        self.unsolved = []
        self.time = 0
        self.stop_time = -1
        self.stop_by_time = False
        self.timeout = timeout

    def set_stop_time(self, stop):
        self.stop_time = stop
        self.partt.stop_time = stop
        self.stop_by_time = False
        self.partt.stop_by_time = False

    def time_check(self):
        if self.partt.stop_by_time or self.stop_by_time or time.time() > self.stop_time:
            self.stop_by_time = True
            return True
        return False

    def sound_derive(self, pconset:List[PCon], p):
        conset = []
        for pcon in pconset:
            if self.time_check():
                return None
            if self.partt.z3.intersect(pcon.predicate, p):
                conset = conset + pcon.constraints
        # print("Sound Derive for {0}: {1}".format(p, pretty_conset_print(conset)))
        return conset

    def complete_derive(self, pconset:List[PCon], p):
        conset = []
        for pcon in pconset:
            if self.time_check():
                return None
            if self.partt.z3.induct(p, pcon.predicate):
                conset = conset + pcon.constraints
        # print("Complete Derive for {0}: {1}".format(p, pretty_conset_print(conset)))
        return conset

    def solve_one_shot(self, pconset:List[PCon]):
        done = {}
        self.partt.init_partt(pconset)
        self.partt.one_shot_partt()
        if self.time_check():
            return False
        if globals.DEBUG:
            print("One-Shot: Solving Constraint per partt")
        for predicate in self.partt.parttset:
            if self.time_check():
                return False
            if globals.DEBUG:
                print(".")
            if self.rm.solve(self.sound_derive(pconset, predicate)):  # sound == complete, either is good
                done[predicate] = self.rm.solution
            else:
                self.unsolved = [predicate]
                return False
        self.solution = done
        return True

    def solve_early_accept(self, pconset:List[PCon])->bool:
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print("#partt:" + str(len(self.partt.parttset)))
                print("Early-Accept: Solving Constraints per Partt")
            new_partt = []
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print(".")
                if self.rm.solve(self.sound_derive(pconset, predicate)):
                    done[predicate] = self.rm.solution
                    # print(predicate + ": " + pretty_rm_solution_print(self.rm.solution))
                else:
                    new_partt.append(predicate)
            if not new_partt:
                # early solution is found
                self.solution = done
                return True
            self.partt.parttset = new_partt  # The unfinished partition is passed back to partition algorithm
        self.unsolved = self.partt.parttset
        return False

    def solve_early_reject(self, pconset:List[PCon])->bool:
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print("#partt:" + str(len(self.partt.parttset)))
                print("Early-Reject: Solving Constraints per Partt")
            done = {}
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print(".")
                if self.rm.solve(self.complete_derive(pconset, predicate)):
                    done[predicate] = self.rm.solution
                    # print predicate + ": " + pretty_rm_solution_print(self.rm.solution)
                else:
                    self.unsolved = [predicate]
                    return False
        self.solution = done
        return True

    def solve_hybrid(self, pconset:List[PCon])->bool:
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print("#partt:" + str(len(self.partt.parttset)))
                print("Hybrid: Solving Constraints per Partt")
            new_partt = []
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print(".")
                if self.rm.solve(self.sound_derive(pconset, predicate)):
                    done[predicate] = self.rm.solution
                else:
                    if not self.rm.solve(self.complete_derive(pconset, predicate)):
                        # early rejection found
                        self.unsolved = [predicate]
                        return False
                    new_partt.append(predicate)
            if not new_partt:
                # early solution found
                self.solution = done
                return True
            self.partt.parttset = new_partt  # The unfinished partition is passed back to partition algorithm
        # If reach here: the partition algorithm does not reach an equivalent state at the last iteration
        raise PartitionNotEquivalentAtEndError

    def solve_constraint(self, pconset:List[PCon], approach=globals.EARLY_ACCETP_APPROACH)->bool:
        self.partt.z3.init_pconset(pconset)

        print(self.partt.__class__.__name__ + " Partition, " + globals.Approach[approach] + " Approach:")

        solve = False
        for app in globals.Approach.keys():
            if approach == app:
                t_start = time.time()
                self.set_stop_time(t_start + 60*self.timeout)
                solve = getattr(self, "solve_"+globals.Approach[app].lower())(pconset)
                self.time = time.time() - t_start
                break

        print("\nExecution Time: {0:.5f}".format(self.time))
        if solve:
            print("Solution:")
            print(self.pretty_solution())
        else:
            print("Unsatisfiable:")
            for counter in self.unsolved:
                print(counter)
        return solve

    def pretty_solution(self):
        msg = "{\n"
        for predicate in self.solution:
            msg += "\t" + predicate + " => " + RMSolver.pretty_solution(self.solution[predicate]) + "\n"
        msg += "}"
        return msg


class TestBaseSolver(unittest.TestCase):
    def test_solver_combination(self):
        solver = PartitionDerivationSolver(CombinationPartition())
        parser = CoreConstraintParser()
        for i in globals.Approach.keys():
            self.assertTrue(solver.solve_constraint(parser.parse('''True => L <: ax And az <: ax; dddd>0 => H <: ay; Not(dddd>0) => L <: ay;
            dddd>0 => H<: ay; dddd<0=> ay<:ax; True=>ax<:L'''), i))
        for i in globals.Approach.keys():
            self.assertFalse(solver.solve_constraint(parser.parse('''a>0=>H<:a And H<:c; a<0 => a<:L And L <: b; b>0=>H <:b; And(bbbb<0, (dddd<0)) => b<:L;
            c>0=>H<:c And L<:a; c<0=>c<:L'''), i))
    def test_solver_sequential(self):
        solver = PartitionDerivationSolver(SequentialPartition())
        parser = CoreConstraintParser()
        for i in globals.Approach.keys():
            self.assertTrue(solver.solve_constraint(parser.parse('''True => L <: ax And az <: ax; d>0 => H <: ay; Not(d>0) => L <: ay;
            d>0 => H<: ay; d<0=> ay<:ax; True=>ax<:L'''), i))
        for i in globals.Approach.keys():
            self.assertFalse(solver.solve_constraint(parser.parse('''a>0=>H<:a And H<:c; a<0 => a<:L And L <: b; b>0=>H <:b; And(b<0, (d<0)) => b<:L;
            c>0=>H<:c And L<:a; c<0=>c<:L'''), i))


if __name__ == '__main__':
#     if len(sys.argv) <= 1:
#         print ("Usage: test_solver.py [test_file] -op [op]")
#         print ("\t [test_file]: test file .con; use \'all\' to run all the file under tests/")
#         print ("\t -partt [0-1]: -partt [0-1]: specifying partition algorithm: 0=sequential,")
#         print ("\t\t\t1=combinational; if not specified, it tests all the partt ")
#         print ("\t\t\talgorithms")
#         print ("\t -appr [0-3]: specifying approaches: 0=hybrid, 1=early-accept, 2=one-shot,")
#         print ("\t\t\t3=early-reject; if not specified, it tests [0,1,2] approaches.")
#         print ("\t -time  i : specifying time-out minutes; default i=3 min.")
#         print ("\t -debug [0-1] : print debug message; default 1 with debug message on")

#     else:
#         file_name = output_file_name("Test1")
#         # print file_name
#         # try:
#         partt = globals.ParttAlg.keys()
#         appr = globals.Approach.keys()
#         #appr.pop(globals.EARLY_REJECT_APPROACH)
        
#         for i in range(2, len(sys.argv)):
#             if sys.argv[i] == "-partt":
#                 partt = [int(sys.argv[i+1])]
#                 print (partt)
#             elif sys.argv[i] == "-appr":
#                 appr = [int(sys.argv[i+1])]
#             elif sys.argv[i] == "-time":
#                 globals.STOP_MIN = float(sys.argv[i+1])
#             elif sys.argv[i] == "-debug":
#                 globals.DEBUG = int(sys.argv[i+1])

#         file_test = sys.argv[1]
#         if sys.argv[1] == "all":
#             file_test = [TEST_DIR + file for file in os.listdir(TEST_DIR)]
#             for test_file_name in file_test:
#                 test_file(test_file_name, partt, appr)
#         else:
#             test_file(file_test, partt, appr)

#         # save result:
#         if files:
#             store_result_file(file_name, files, number, partt_alg, perform)

        # if sys.argv[1] == 'all':
        #     plot_line_chart(file_name + plt_ext, partt, appr, number, partt_alg, perform)
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)
    #unittest.main()
    #unittest.main(verbosity=2)

