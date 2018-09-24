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
from z3 import *
from lexer import VariableToken
import re
import time


class Z3Supp:
    time_init = 0
    time_intersection = 0
    time_induct = 0
    time_valid = 0

    def __init__(self):
        self.reserved = {'And', 'Or', 'Not', 'True', 'False'}
        self.varset = set()
        self.declare = ""
        self.inductset = {}
        self.and_set = {}

    def init_pconset(self, pconset):
        t_start = time.time()
        # print "Initialize the solver...And_Dict..."
        for pcon in pconset:
            self.__declare_vars(pcon.predicate)
        self.time_init = time.time() - t_start
        # exec self.declare
        # print "Initialization for And_Dict Finished."

    # def check_intersection(self, p1, p2):
    #     and_list = list(set(p1+p2))
    #     result = True
    #     for index in range(1, len(and_list)):
    #         cur = False
    #         if (and_list[0], and_list[index]) in self.and_set:
    #             cur = self.and_set[(and_list[0], and_list[index])]
    #         else:
    #             cur = self.and_set[(and_list[index], and_list[0])]
    #         result = result and cur
    #         if not cur:
    #             return False

    # def __generate_key(self, p1, p2):
    #     return p1+"_"+p2

    def __declare_vars(self, p):
        varlist = re.findall(VariableToken.lex_reg, p)
        for var in varlist:
            if var not in self.reserved and var not in self.varset:
                self.varset.add(var)
                declare = "{0} = Int(\'{0}\')".format(var)
                # print declare
                self.declare += declare+"\n"

    def intersect(self, p1, p2):
        t_start = time.time()
        if p1 == "False" or p2 == "False":
            return False
        if p1 == "True" or p2 == "True":
            return True

        # key = self.__generate_key(p1, p2)
        # if key in self.interset:
        #     return self.interset[key]
        # else:
        #     key = self.__generate_key(p2, p1)
        #     if key in self.interset:
        #         return self.interset[key]

        # self.__declare_vars(p1)
        # self.__declare_vars(p2)
        exec self.declare
        s = Solver()
        stmt1 = "s.add({0})".format(p1)
        stmt2 = "s.add({0})".format(p2)
        # print stmt1
        # print stmt2
        eval(stmt1)
        eval(stmt2)

        # self.interset[key] = (s.check() == sat)
        self.time_intersection += time.time()-t_start
        return s.check() == sat

    def induct(self, p1, p2):
        t_start = time.time()
        if p2 == "True" or p1 == "False":
            return True

        # key = self.__generate_key(p1, p2)
        # if key in self.inductset:
        #     return self.inductset[key]

        # self.__declare_vars(p1)
        # self.__declare_vars(p2)
        exec self.declare
        s = Solver()
        stmt1 = "s.add({0})".format(p1)
        stmt2 = "s.add(Not({0}))".format(p2)
        eval(stmt1)
        eval(stmt2)
        self.time_induct += time.time() - t_start
        return s.check() == unsat

    def not_p_string(self, p):
        if p == "True":
            return "False"
        if p == "False":
            return "True"
        if len(p) > 5 and p[0:4] == "Not(" and p[-1] == ')':
            return p[4:-1]
        return "Not({0})".format(p)

    def and_predicates(self, *predicates):
        valid = []
        for p in predicates:
            if p == "False" or not self.valid_p(p):
                return "False"
            elif p != "True" and p not in valid:
                if len(p) > 5 and p[0:4] == "And(" and p[-1] == ")":
                    p = p[4:-1]
                valid.append(p)

        if len(valid) == 0:
            return "True"
        elif len(valid) == 1:
            return valid[0]
        else:
            result = "And(" + valid[0]
            for p in valid[1:]:
                result += ", " + p
            result += ")"
            return result

    # def and_p1_p2(self, p1, p2):
    #     if p1 == "False" or p2 == "False":
    #         return "False"
    #     if p1 == "True" or p1 == p2:
    #         return p2
    #     elif p2 == "True":
    #         return p1
    #     else:
    #         if len(p1) > 5 and p1[0:4] == "And(" and p1[-1] == ")":
    #             p1 = p1[4:-1]
    #         if len(p2) > 5 and p2[0:4] == "And(" and p2[-1] == ")":
    #             p2 = p2[4:-1]
    #         return "And({0}, {1})".format(p1, p2)

    def valid_p(self, p):
        t_start = time.time()
        self.__declare_vars(p)
        exec self.declare
        s = Solver()
        stmt1 = "s.add({0})".format(p)
        eval(stmt1)
        self.time_valid += time.time()-t_start
        return s.check() == sat


if __name__ == '__main__':
    z3 = Z3Supp()
    print z3.intersect("And(x+y>5, x==5)", "a+y<4+6")
    print z3.induct("x>5", "x>0")
    print z3.induct("x>5", "x>10")
    print z3.intersect("And(x+y>5, (x==5))", "a+y<4+6")
    # print z3.induct("(And (x>5) (x>10))")
    s = Solver()
    s.add(parse_smt2_string('(declare-const x Int) (assert (< x 10)) (assert (> x 0))'))
    # s.add(parse_smt2_string('(declare-const x Int) (assert (> x 0))'))
    print s.check()