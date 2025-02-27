#!/usr/bin/env python3
# python >= 3.7

from z3 import *
from lexer import VariableToken
import re
import time

import logging
import unittest

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
        logging.debug("Initialize the solver...And_Dict...")
        for pcon in pconset:
            self.__declare_vars(pcon.predicate)
        self.time_init = time.time() - t_start
        # exec self.declare
        logging.debug("Initialization for And_Dict Finished.")

    def __declare_vars(self, p): # find the variables and declare them as int in Z3
        varlist = re.findall(VariableToken.lex_reg, p)
        for var in varlist:
            if var not in self.reserved and var not in self.varset:
                self.varset.add(var)
                declare = "{0} = Int(\'{0}\')".format(var)
                self.declare += declare+"\n"

    def intersect(self, p1, p2): # Check if p1 and p2 intersects
        t_start = time.time()
        #  Skip the trivial cases so that no Z3 processing
        if p1 == "False" or p2 == "False":
            return False
        if p1 == "True" or p2 == "True":
            return True

        self.__declare_vars(p1)
        self.__declare_vars(p2)
        exec(self.declare)
        s = Solver()
        stmt1 = "s.add({0})".format(p1)
        stmt2 = "s.add({0})".format(p2)
        eval(stmt1)
        eval(stmt2)

        self.time_intersection += time.time()-t_start
        return s.check() == sat

    def induct(self, p1, p2): # check if p1 => p2, returns a bool
        t_start = time.time()
        if p2 == "True" or p1 == "False":
            return True

        self.__declare_vars(p1)
        self.__declare_vars(p2)
        exec(self.declare)
        s = Solver()
        stmt1 = "s.add({0})".format(p1)
        stmt2 = "s.add(Not({0}))".format(p2)
        eval(stmt1)
        eval(stmt2)
        self.time_induct += time.time() - t_start
        return s.check() == unsat

    def not_p_string(self, p): # return not p
        if p == "True":
            return "False"
        if p == "False":
            return "True"
        if len(p) > 5 and p[0:4] == "Not(" and p[-1] == ')':
            return p[4:-1]
        return "Not({0})".format(p)

    def and_predicates(self, *predicates): # return p1 AND p2 AND ...
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

    def valid_p(self, p): # Check whether a predicate is still satisifiable 
        t_start = time.time()
        self.__declare_vars(p)
        exec(self.declare)
        s = Solver()
        stmt1 = "s.add({0})".format(p)
        eval(stmt1)
        self.time_valid += time.time()-t_start
        return s.check() == sat

class TestZ3Supp(unittest.TestCase):
    def test_z3Installation(self):
        s = Solver()
        s.add(parse_smt2_string('(declare-const x Int) (assert (< x 10)) (assert (> x 0))'))
        self.assertEqual(str(s.check()), 'sat')
    def test_z3Supp_induct(self):
        z3 = Z3Supp()
        self.assertTrue(z3.induct("x>5", "x>0"))
        self.assertFalse(z3.induct("x>5", "x>10"))
    def test_z3Supp_intersect(self):
        z3 = Z3Supp()
        self.assertTrue(z3.intersect("x>5", "x>0"))
        self.assertFalse(z3.intersect("x>5", "x<0"))
        self.assertTrue(z3.intersect("x>=5", "x<=5"))
        self.assertFalse(z3.intersect("x>5", "x<5"))
        self.assertTrue(z3.intersect("And(x+y>5, x==5)", "a+y<4+6"))
    def test_z3Supp_valid_p(self):
        z3 = Z3Supp()
        self.assertTrue(z3.valid_p("And(x>5, x>0)"))
        self.assertFalse(z3.valid_p("And(x>5, Not(x>0))"))
    def test_z3Supp_not_p_string(self):
        z3 = Z3Supp()
        self.assertFalse(z3.induct("x>5", z3.not_p_string("x>0")))
        self.assertTrue(z3.induct(z3.not_p_string("x>5"), z3.not_p_string("x>10")))
    def test_z3Supp_and_predicates(self):
        z3 = Z3Supp()
        self.assertTrue(z3.valid_p(z3.and_predicates('x>5', 'y>0')))
        self.assertFalse(z3.valid_p(z3.and_predicates('x>5', 'Not(x>0)')))
        self.assertTrue(z3.valid_p(z3.and_predicates('x>5', 'x>0', 'y>=0', 'y<=0')))
        self.assertFalse(z3.valid_p(z3.and_predicates('x>5', 'x>0', 'y>=0', 'y<0')))
    def test_variable_name_extraction(self):
        z3 = Z3Supp()
        self.assertTrue(z3.valid_p("And(x__1>5, x__1>0)"))
        self.assertFalse(z3.valid_p("And(x__1>5, x__1<0)"))
        self.assertFalse(z3.valid_p("And(x_very____long_name_1__variable_name>5, x_very____long_name_1__variable_name<0)"))
        self.assertTrue(z3.valid_p("And(x_very____long_name_1__variable_name>5, x_very____long_name_2__variable_name<0)"))

if __name__ == '__main__':
    unittest.main(verbosity=2)
