#     This file is part of Derivation Solver. Derivation Solver provides
#     implementation of derivation solvers for dependent type inference.
# 
#     Copyright (C) 2018  Peixuan Li
# 
#     Derivation Solver is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Derivation Solver is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
# 
from lattice import *
from partt import *
from rm_solver import RMSolver, pretty_rm_solution
import time
import globals


class PartitionDerivationSolver:
    def __init__(self, partt=SequentialPartition(), lat=TwoPointLattice()):
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

    def sound_derive(self, pconset, p):
        conset = []
        for pcon in pconset:
            if self.time_check():
                return None
            if self.partt.z3.intersect(pcon.predicate, p):
                conset = conset + pcon.constraints
        # print "Sound Derive for {0}: {1}".format(p, pretty_conset_print(conset))
        return conset

    def complete_derive(self, pconset, p):
        conset = []
        for pcon in pconset:
            if self.time_check():
                return None
            if self.partt.z3.induct(p, pcon.predicate):
                conset = conset + pcon.constraints
        # print "Complete Derive for {0}: {1}".format(p, pretty_conset_print(conset))
        return conset

    # def check_partition_final_equivalence(self, pconset):
    #     self.partt.init_partt(pconset)
    #     while not self.partt.stop_partt:
    #         self.partt.next_partt()
    #     for predicate in self.partt.parttset:
    #         if self.sound_derive(pconset, predicate) != self.complete_derive(pconset, predicate):
    #             return False
    #     return True

    def solve_one_shot(self, pconset):
        done = {}
        self.partt.init_partt(pconset)
        self.partt.one_shot_partt()
        if self.time_check():
            return False
        if globals.DEBUG:
            print "One-Shot: Solving Constraint per partt",
        for predicate in self.partt.parttset:
            if self.time_check():
                return False
            if globals.DEBUG:
                print ".",
            if self.rm.solve(self.sound_derive(pconset, predicate)):  # sound == complete, either is good
                done[predicate] = self.rm.solution
            else:
                self.unsolved = [predicate]
                return False
        self.solution = done
        return True

    def solve_early_accept(self, pconset):
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print "#partt:" + str(len(self.partt.parttset))
                print "Early-Accept: Solving Constraints per Partt",
            new_partt = []
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print ".",
                if self.rm.solve(self.sound_derive(pconset, predicate)):
                    done[predicate] = self.rm.solution
                    # print predicate + ": " + pretty_rm_solution_print(self.rm.solution)
                else:
                    new_partt.append(predicate)
            if not new_partt:
                # early solution is found
                self.solution = done
                return True
            self.partt.parttset = new_partt  # The unfinished partition is passed back to partition algorithm
        self.unsolved = self.partt.parttset
        return False

    def solve_early_reject(self, pconset):
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print "#partt:" + str(len(self.partt.parttset))
                print "Early-Reject: Solving Constraints per Partt",
            done = {}
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print ".",
                if self.rm.solve(self.complete_derive(pconset, predicate)):
                    done[predicate] = self.rm.solution
                    # print predicate + ": " + pretty_rm_solution_print(self.rm.solution)
                else:
                    self.unsolved = [predicate]
                    return False
        self.solution = done
        return True

    def solve_hybrid(self, pconset):
        done = {}
        self.partt.init_partt(pconset)
        while not self.partt.stop_partt:
            self.partt.next_partt()
            if self.time_check():
                return False
            if globals.DEBUG:
                print "#partt:" + str(len(self.partt.parttset))
                print "Hybrid: Solving Constraints per Partt",
            new_partt = []
            for predicate in self.partt.parttset:
                if self.time_check():
                    return False
                if globals.DEBUG:
                    print ".",
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

    def solve_constraint(self, pconset, approach=globals.EARLY_ACCETP_APPROACH):
        self.partt.z3.init_pconset(pconset)

        print self.partt.__class__.__name__ + " Partition, " + globals.Approach[approach] + " Approach:"

        solve = False
        for app in globals.Approach.keys():
            if approach == app:
                t_start = time.time()
                self.set_stop_time(t_start + 60*globals.STOP_MIN)
                solve = getattr(self, "solve_"+globals.Approach[app].lower())(pconset)
                self.time = time.time() - t_start
                break

        print "\nExecution Time: {0:.5f}".format(self.time)
        if solve:
            print "Solution:"
            print self.pretty_solution()
        else:
            print "Unsatisfiable:"
            for counter in self.unsolved:
                print counter

    def pretty_solution(self):
        msg = "{\n"
        for predicate in self.solution:
            msg += "\t" + predicate + " => " + pretty_rm_solution(self.solution[predicate]) + "\n"
        msg += "}"
        return msg


if __name__ == '__main__':
    # solver = PartitionDerivationSolver()
    solver = PartitionDerivationSolver(CombinationPartition())

    for i in globals.Approach.keys():
        solver.solve_constraint('''True => L <: ax And az <: ax; d>0 => H <: ay; Not(d>0) => L <: ay;
            d>0 => H<: ay; d<0=> ay<:ax; True=>ax<:L''', i)

    for i in globals.Approach.keys():
        solver.solve_constraint('''a>0=>H<:a; a<0 => a<:L And L <: b; b>0=>H <:b; And(b<0, (d<0)) => b<:L;
                c>0=>H<:c And L<:a; c<0=>c<:L''', i)

    for i in globals.Approach.keys():
        solver.solve_constraint('''a>0=>H<:a And H<:c; a<0 => a<:L And L <: b; b>0=>H <:b; And(b<0, (d<0)) => b<:L;
            c>0=>H<:c And L<:a; c<0=>c<:L''', i)

