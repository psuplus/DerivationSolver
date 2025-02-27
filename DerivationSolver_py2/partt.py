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
from z3supp import Z3Supp
import itertools as it
import time
import globals


class PartitionNotEquivalentAtEndError(Exception):
    pass


class PartitionContext:
    def __init__(self):
        self.parttset = []
        self.stop_partt = True
        self.z3 = Z3Supp()
        self.predicates = []
        self.stop_time = -1
        self.stop_by_time = False

    def time_check(self):
        if self.stop_by_time or time.time() > self.stop_time:
            self.stop_by_time = True
            return True
        return False

    def refine_partt(self, partt, p):
        not_p = self.z3.not_p_string(p)
        if not partt:
            cur = []
            if self.z3.valid_p(p):
                cur.append(p)
            if self.z3.valid_p(not_p):
                cur.append(not_p)
            return cur
        result = []
        for pp in partt:
            if self.time_check():
                return None
            if (not self.z3.intersect(pp, p)) or (not self.z3.intersect(pp, not_p)):
                result.append(pp)
            elif self.z3.induct(p, pp):
                result.append(p)
                result.append(self.z3.and_predicates(pp, not_p))
            else:
                result.append(self.z3.and_predicates(pp, p))
                result.append(self.z3.and_predicates(pp, not_p))
        return result

    def init_partt(self, pconset):
        self.predicates = []
        for pcon in pconset:
            self.predicates.append(pcon.predicate)

    def next_partt(self):
        pass

    def one_shot_partt(self):
        self.parttset = []
        for p in self.predicates:
            if self.time_check():
                return None
            if globals.DEBUG:
                print "#partt: " + str(len(self.parttset))
            self.parttset = self.refine_partt(self.parttset, p)
        self.stop_partt = True


class SequentialPartition(PartitionContext):
    def __init__(self):
        PartitionContext.__init__(self)
        self.state = 0

    def init_partt(self, pconset):
        self.predicates = []
        for pcon in pconset:
            self.predicates.append(pcon.predicate)
        self.parttset = []
        self.stop_partt = False
        self.state = 0

    def next_partt(self):
        if self.state == 0:
            self.state += 1
            self.parttset = ["True"]
            return
        self.parttset = self.refine_partt(self.parttset, self.predicates[self.state-1])  # use only the unfinished
        self.state += 1
        self.stop_partt = (self.state > len(self.predicates))


class CombinationPartition(PartitionContext):
    def __init__(self):
        PartitionContext.__init__(self)
        self.state = 0
        self.predicates = []
        self.combination = []

    def init_partt(self, pconset):
        self.predicates = []
        for pcon in pconset:
            self.predicates.append(pcon.predicate)
        self.stop_partt = False
        self.state = 0
        self.combination = []

    def next_partt(self):
        if self.state == 0:
            self.parttset = ["True"]
            self.state += 1
            return
        if not self.combination:
            for comb in it.combinations(self.predicates, self.state):
                self.combination.append(comb)
            self.state += 1
            # if globals.DEBUG:
            #     print str(self.state) + "\t" + str(self.combination)
        partt = self.combination.pop()
        if globals.DEBUG:
            print "Combinations left at level " + str(self.state-1) + " :\t" + str(len(self.combination))
        self.parttset = []  # forget the previous level result
        for p in partt:
            if self.time_check():
                return None
            if globals.DEBUG:
                print "#partt: "+ str(len(self.parttset))
            self.parttset = self.refine_partt(self.parttset, p)
        self.stop_partt = (self.state > len(self.predicates))


# class OpCombinationPartition(PartitionContext):
#     def __init__(self):
#         PartitionContext.__init__(self)
#         self.state = 0
#         self.predicates = []
#         self.combination = []
#
#     def init_partt(self, pconset):
#         self.predicates = []
#         for pcon in pconset:
#             self.predicates.append(pcon.predicate)
#         self.stop_partt = False
#         self.state = 0
#         self.combination = []
#
#     def next_partt(self):
#         if self.state == 0:
#             self.parttset = ["True"]
#             self.state += 1
#             return
#         if not self.combination:
#             for comb in it.combinations(self.predicates, self.state):
#                 self.combination.append(comb)
#             self.state += 1
#         partt = self.combination.pop()
#
#         for p in partt:
#             if self.time_check():
#                 return None
#             self.parttset = self.refine_partt(self.parttset, p)
#         self.stop_partt = (self.state == len(self.predicates))  # there will be only one comb in the last level

