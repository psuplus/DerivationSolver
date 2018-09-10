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

    def check_sub(self, low, high):
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


def test_lattice_print(l1, l2, output, result, msg):
    if output == result:
        print('checking {0} {2} {1} - PASSED'.format(str(l1), str(l2), msg))
    else:
        print('checking {0} {4} {1} - FAiled with output {2}, not {3}'.format(str(l1), str(l2), str(output), str(result), msg))


def test_lattice_join(lattice, l1, l2, result):
    test_lattice_print(l1, l2, lattice.join(l1, l2), result, "join")


def test_lattice_sub(lattice, l1, l2, result):
    test_lattice_print(l1, l2, lattice.check_sub(l1, l2), result, "<:")


if __name__ == '__main__':
    l1 = Label("L1")
    l2 = Label("L2")
    l3 = Label("L3")
    l4 = Label("L4")
    l5 = Label("L5")
    l6 = Label("L6")
    lattice = Lattice()
    lattice.add_sub(l5, l4)
    lattice.add_sub(l2, l5)
    lattice.add_sub(l2, l4)
    lattice.add_sub(l2, l3)
    lattice.add_sub(l4, l6)
    lattice.add_sub(l1, l3)
    lattice.add_sub(l1, l2)
    lb = lattice.bot
    lt = lattice.top

    print("Testing latticee Model:" + str(lattice))

    for l in lattice.labels:
        print str(l)

    print lattice.lowest

    # test_lattice_sub(lattice, l1, l2, False)
    # test_lattice_sub(lattice, l1, l3, True)
    # test_lattice_sub(lattice, l1, l4, False)
    # test_lattice_sub(lattice, l1, l5, False)
    # test_lattice_sub(lattice, l1, l6, False)
    # test_lattice_sub(lattice, l2, l3, True)
    # test_lattice_sub(lattice, l2, l4, True)
    # test_lattice_sub(lattice, l2, l5, False)
    # test_lattice_sub(lattice, l2, l6, True)
    # test_lattice_sub(lattice, l3, l4, False)
    # test_lattice_sub(lattice, l3, l5, False)
    # test_lattice_sub(lattice, l3, l6, False)
    # test_lattice_sub(lattice, l4, l6, True)
    # test_lattice_sub(lattice, l4, l5, False)
    # test_lattice_sub(lattice, l5, l6, True)
    #
    # test_lattice_sub(lattice, l5, lt, True)
    # test_lattice_sub(lattice, lt, l6, False)
    # test_lattice_sub(lattice, l5, lb, False)
    # test_lattice_sub(lattice, lb, l6, True)
    #
    # test_lattice_join(lattice, l1, l2, l3)
    # test_lattice_join(lattice, l1, l3, l3)
    # test_lattice_join(lattice, l1, l4, lt)
    # test_lattice_join(lattice, l1, l5, lt)
    # test_lattice_join(lattice, l1, l6, lt)
    # test_lattice_join(lattice, l2, l3, l3)
    # test_lattice_join(lattice, l2, l4, l4)
    # test_lattice_join(lattice, l2, l5, l4)
    # test_lattice_join(lattice, l2, l6, l6)
    # test_lattice_join(lattice, l3, l4, lt)
    # test_lattice_join(lattice, l3, l5, lt)
    # test_lattice_join(lattice, l3, l6, lt)
    # test_lattice_join(lattice, l4, l6, l6)
    # test_lattice_join(lattice, l4, l5, l4)
    # test_lattice_join(lattice, l5, l6, l6)
    #
    # test_lattice_join(lattice, lt, l6, lt)
    # test_lattice_join(lattice, lb, l6, l6)
    # test_lattice_join(lattice, l4, lb, l4)
    # test_lattice_join(lattice, l5, lt, lt)
    #
    # test_lattice_join(lattice, lb, lt, lt)
    # test_lattice_join(lattice, lt, lb, lt)
    # test_lattice_join(lattice, lt, lt, lt)
    # test_lattice_join(lattice, lb, lb, lb)
