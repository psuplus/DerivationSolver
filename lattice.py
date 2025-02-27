#!/usr/bin/env python3
# python >= 3.7

import logging
import unittest

from parser import Label

class Lattice:
    def __init__(self):
        self.sub = []
        self.top = Label("Top")
        self.bot = Label("Bot")
        self.lowest = self.bot
        self.labels = []

    def add_sub(self, low, high):
        self.sub.append((low, high))
        if low not in self.labels:
            self.labels.append(low)
        if high not in self.labels:
            self.labels.append(high)
        if self.lowest == self.bot or self.check_sub(low, self.lowest):
            self.lowest = low

    def check_sub(self, low, high)->bool:
        if low == high or low == self.bot or high == self.top:
            return True
        elif low == self.top or high == self.bot:
            return False
        work = [high]
        while bool(work):
            can = work.pop(0)
            for r in self.sub:
                if (r[1] == can) and (r[0] == low):
                    return True
                elif r[1] == can:
                    work.append(r[0])
        return False

    def join(self, l1, l2):
        if l1 == l2 or self.check_sub(l1, l2):
            return l2
        elif self.check_sub(l2, l1):
            return l1
        else:
            work = [l1]
            while bool(work):
                can = work.pop(0)
                for r in self.sub:
                    if (r[0] == can) and self.check_sub(l2, r[1]):
                        return r[1]
                    elif r[0] == can:
                        work.append(r[1])
            return self.top

    def __str__(self):
        result = "Model"
        for r in self.sub:
            result = result + ", " + str(r[0]) + "<:" + str(r[1])
        return result


class TwoPointLattice(Lattice):
    def __init__(self):
        Lattice.__init__(self)
        self.add_sub(Label("L"), Label("H"))

class TestLattice(unittest.TestCase):
    def test_lattice_sub(self):
        l1 = Label("L1")
        l2 = Label("L2")
        l3 = Label("L3")
        l4 = Label("L4")
        l5 = Label("L5")
        l6 = Label("L6")
        lattice = Lattice()
        lattice.add_sub(l5, l4)
        lattice.add_sub(l2, l4)
        lattice.add_sub(l2, l3)
        lattice.add_sub(l4, l6)
        lattice.add_sub(l1, l3)
        lb = lattice.bot
        lt = lattice.top
        self.assertTrue(lattice.check_sub(l1, l2)==False)
        self.assertTrue(lattice.check_sub(Label("L1"), l3)==True)
        self.assertTrue(lattice.check_sub(l1, l4)==False)
        self.assertTrue(lattice.check_sub(l1, l5)==False)
        self.assertTrue(lattice.check_sub(l1, l6)==False)
        self.assertTrue(lattice.check_sub(Label("L2"), l3)==True)
        self.assertTrue(lattice.check_sub(l2, l4)==True)
        self.assertTrue(lattice.check_sub(l2, Label("L5"))==False)
        self.assertTrue(lattice.check_sub(l2, l6)==True)
        self.assertTrue(lattice.check_sub(Label("L3"), l4)==False)
        self.assertTrue(lattice.check_sub(l3, l5)==False)
        self.assertTrue(lattice.check_sub(l3, l6)==False)
        self.assertTrue(lattice.check_sub(Label("L4"), Label("L6"))==True)
        self.assertTrue(lattice.check_sub(l4, l5)==False)
        self.assertTrue(lattice.check_sub(l5, l6)==True)
        self.assertTrue(lattice.check_sub(l5, lt)==True)
        self.assertTrue(lattice.check_sub(lt, l6)==False)
        self.assertTrue(lattice.check_sub(l5, lb)==False)
        self.assertTrue(lattice.check_sub(lb, l6)==True)

    def test_lattice_join(self):
        l1 = Label("L1")
        l2 = Label("L2")
        l3 = Label("L3")
        l4 = Label("L4")
        l5 = Label("L5")
        l6 = Label("L6")
        lattice = Lattice()
        lattice.add_sub(l5, l4)
        lattice.add_sub(l2, l4)
        lattice.add_sub(l2, l3)
        lattice.add_sub(l4, l6)
        lattice.add_sub(l1, l3)
        lb = lattice.bot
        lt = lattice.top
        self.assertTrue(lattice.join(Label("L1"), l2)==l3)
        self.assertTrue(lattice.join(l1, l3)==l3)
        self.assertTrue(lattice.join(l1, l4)==lt)
        self.assertTrue(lattice.join(l1, l5)==lt)
        self.assertTrue(lattice.join(l1, l6)==lt)
        self.assertTrue(lattice.join(l2, Label("L3"))==l3)
        self.assertTrue(lattice.join(l2, l4)==l4)
        self.assertTrue(lattice.join(l2, l5)==l4)
        self.assertTrue(lattice.join(Label("L2"), l6)==l6)
        self.assertTrue(lattice.join(l3, l4)==lt)
        self.assertTrue(lattice.join(l3, l5)==lt)
        self.assertTrue(lattice.join(l3, l6)==lt)
        self.assertTrue(lattice.join(l3, l6)==lt)
        self.assertTrue(lattice.join(Label("L4"), Label("L5"))==l4)
        self.assertTrue(lattice.join(l4, l6)==l6)
        self.assertTrue(lattice.join(l5, l6)==l6)

        self.assertTrue(lattice.join(lt, Label("L6"))==lt)
        self.assertTrue(lattice.join(lb, l6)==l6)
        self.assertTrue(lattice.join(lb, l4)==l4)
        self.assertTrue(lattice.join(l5, lt)==lt)

        self.assertTrue(lattice.join(lb, lt)==lt)
        self.assertTrue(lattice.join(lt, lb)==lt)
        self.assertTrue(lattice.join(lt, lt)==lt)
        self.assertTrue(lattice.join(lb, lb)==lb)

if __name__ == '__main__':
    unittest.main(verbosity=2)
