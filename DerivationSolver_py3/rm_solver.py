#!/usr/bin/env python3
# python >= 3.7

import logging
import unittest
from typing import Dict, List

from lattice import *
from parser import *


class RMSolver:
    solution:Dict[str, Label]

    def __init__(self, lat):
        self.lattice = lat
        self.solution = {}

    def __get_label(self, solu, expr):
        if expr.name in solu:
            return solu[expr.name]
        elif isinstance(expr, CVar):
            # return self.lattice.bot
            solu[expr.name] = self.lattice.lowest
            return self.lattice.lowest
        else:
            return expr

    def __valid(self, solu, con):
        left = self.__get_label(solu, con.left)
        right = self.__get_label(solu, con.right)
        if left == self.lattice.bot or right == self.lattice.bot:
            return False
        else:
            return self.lattice.check_sub(left, right)

    def solve(self, conset:List[Con])->bool:
        if conset == None:
            return False
        self.solution = {}
        solu = {}
        work = conset[:]
        while bool(work):
            con = work.pop(0)
            if not self.__valid(solu, con):
                if isinstance(con.right, CVar):
                    old_right = self.__get_label(solu, con.right)
                    left = self.__get_label(solu, con.left)
                    if left != self.lattice.bot:
                        solu[con.right.name] = self.lattice.join(old_right, left)
                        for constraint in conset:
                            if constraint.left == con.right:
                                work.append(constraint)
        for cons in conset:
            if not self.__valid(solu, cons):
                return False
        self.solution = solu
        return True
    @staticmethod
    def pretty_solution(rmsolution):
        msg = "{"
        for var in rmsolution:
            msg += var + ": " + str(rmsolution[var]) + "; "
        msg += "}"
        return msg

# def pretty_rm_solution(rmsolution):
#     msg = "{"
#     for var in rmsolution:
#         msg += var + ": " + str(rmsolution[var]) + "; "
#     msg += "}"
#     return msg


# def test_rm_solver(solver, conset):
#     msg = "\nTesting Constraint Set: {"
#     for cons in conset[:-1]:
#         msg = msg + str(cons) + ", "
#     msg = msg + str(conset[-1]) + "}"
#     print(msg)
#     if solver.solve(conset):
#         for var in solver.solution:
#             print(var+": " + str(solver.solution[var]))
#     else:
#         print("Constraint are unsatisfiable")

class TestRMSolver(unittest.TestCase):
    def test_RMSolver(self):
        l1 = Label("L1")
        l2 = Label("L2")
        l3 = Label("L3")
        sub = Op("<:")
        a0 = CVar("a0")
        a1 = CVar("a1")
        a2 = CVar("a2")

        lattic = Lattice()
        lattic.add_sub(l1, l3)
        lattic.add_sub(l2, l3)

        solver = RMSolver(lattic)

        conset = [Con(l1, sub, a0), Con(l2, sub, a1), Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2)]
        self.assertTrue(solver.solve(conset))
        self.assertTrue(solver.solution=={'a0':l1, 'a1':l3, 'a2':l3})

        conset = [Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2),
            Con(l1, sub, a0), Con(l2, sub, a1), Con(a2, sub, l2)]
        self.assertFalse(solver.solve(conset))

        conset = [Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2), Con(l1, sub, a0), Con(l2, sub, a1)]
        self.assertTrue(solver.solve(conset))
        self.assertTrue(solver.solution=={'a0':l1, 'a1':l3, 'a2':l3})

if __name__ == '__main__':
    unittest.main(verbosity=2)
