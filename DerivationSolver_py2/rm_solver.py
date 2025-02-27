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
from parser import *


class RMSolver:
    # solution = {}

    def __init__(self, lat):
        self.lattice = lat
        self.solution = {}

    def __get_label(self, solu, expr):
        if solu.has_key(expr.name):
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

    def solve(self, conset):
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


def pretty_rm_solution(rmsolution):
    msg = "{"
    for var in rmsolution:
        msg += var + ": " + str(rmsolution[var]) + "; "
    msg += "}"
    return msg


def test_rm_solver(solver, conset):
    msg = "\nTesting Constraint Set: {"
    for cons in conset[:-1]:
        msg = msg + str(cons) + ", "
    msg = msg + str(conset[-1]) + "}"
    print(msg)
    if solver.solve_early_accept(conset):
        for var in solver.solution:
            print(var+": " + str(solver.solution[var]))
    else:
        print("Constraint are unsatisfiable")


if __name__ == '__main__':
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

    rm = RMSolver(lattic)

    conset = [Con(l1, sub, a0), Con(l2, sub, a1), Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2)]
    test_rm_solver(rm, conset)

    conset = [Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2), Con(l1, sub, a0), Con(l2, sub, a1)]
    test_rm_solver(rm, conset)

    conset = [Con(a0, sub, a1), Con(a0, sub, a2), Con(a1, sub, a2),
              Con(l1, sub, a0), Con(l2, sub, a1), Con(a2, sub, l2)]
    test_rm_solver(rm, conset)
