#!/usr/bin/env python3
# python >= 3.7

import logging
import unittest
from typing import List

from lexer import *

class Expr:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Expr) and self.name == other.name

    def __str__(self):
        return self.name


class Label(Expr):
    def __str__(self):
        return self.name+"_LABEL_"


class CVar(Expr):
    pass


class Op:
    def __init__(self, op):
        self.op = op

    def __str__(self):
        return self.op

    def __eq__(self, other):
        return isinstance(other, Op) and self.op == other.op


class Con:
    def __init__(self, l, o, r):
        self.left = l
        self.right = r
        self.op = o

    def __str__(self):
        return str(self.left) + str(self.op) + str(self.right)

    def __eq__(self, other):
        return isinstance(other, Con) and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.__str__())

class PCon:
    def __init__(self, p, c):
        self.predicate = p
        self.constraints = c

    def __str__(self):
        msg=""
        if self.constraints:
            msg = "{"
            for cons in self.constraints[:-1]:
                msg = msg + str(cons) + ", "
            msg = msg + str(self.constraints[-1]) + "}"
        else:
            msg = "{}"
        return self.predicate + "=>" + msg

    def __eq__(self, other):
        if isinstance(other, PCon):
            return set(self.constraints).issuperset(set(other.constraints)) and set(self.constraints).issubset(set(other.constraints))
        return False


class CoreConstraintParser:
    def __init__(self, labels=["H", "L"]):
        self.lexer = Lexer()
        self.labels = labels
        self.init_lexer()

    def init_lexer(self):
        self.lexer.add_tokens(NoneToken(), AndToken(), SubToken(), SemiToken(), VariableToken())

    def generate_constraint(self, t_exp1, t_sub, t_exp2)->Con:
        if not (isinstance(t_sub, SubToken) and isinstance(t_exp1, VariableToken)
                and isinstance(t_exp2, VariableToken)):
            return None
        exp1 = CVar(t_exp1.token_string)
        exp2 = CVar(t_exp2.token_string)
        if t_exp1.token_string in self.labels:
            exp1 = Label(t_exp1.token_string)
        if t_exp2.token_string in self.labels:
            exp2 = Label(t_exp2.token_string)
        return Con(exp1, Op(t_sub.token_string), exp2)

    def pre_process(self, input_str:str)->str:
        return input_str

    def post_process(self, pconset:List[PCon])->List[PCon]:
        return pconset

    def generate_conset(self, input_str:str)->List[Con]:
        cons = self.lexer.tokenize(input_str)
        conset = []
        for t_exp1, t_sub, t_exp2, t_sep in (cons[i:i + 4] for i in range(0, len(cons) // 4 * 4 , 4)):
            constr = self.generate_constraint(t_exp1, t_sub, t_exp2)
            if constr:
                conset.append(constr)
        i = len(cons) // 4 * 4
        if len(cons) == i + 3:
            constr = self.generate_constraint(cons[i], cons[i + 1], cons[i + 2])
            if constr:
                conset.append(constr)
        return conset

    def generate_predicate(self, input_str:str)->str:
        return input_str.strip()

    def parse(self, input_str:str)->List[PCon]:
        input_str = self.pre_process(input_str)

        constraints = [re.split(SatToken().lex_reg, c_tokens) for c_tokens in re.split(SemiToken().lex_reg, input_str)]

        pconset = []
        for c in constraints:
            pred = "True"
            conset = []
            if len(c) == 2:
                pred = self.generate_predicate(c[0])
                conset = self.generate_conset(c[1])
            elif len(c) == 1:  # add True if no predicate specified
                conset = self.generate_conset(c[0])
            if conset:
                pconset.append(PCon(pred, conset))

        # merge the same predicate cases
        pconset_op = []
        predicates_dic = {}
        for pcon in pconset:
            if pcon.predicate in predicates_dic:
                predicates_dic[pcon.predicate] += pcon.constraints
            else:
                predicates_dic[pcon.predicate] = pcon.constraints
        for key in predicates_dic:
            pconset_op.append(PCon(key, list(set(predicates_dic[key])))) # remove redundents

        return self.post_process(pconset_op)

class TestPaser(unittest.TestCase):
    def check_same_pconset(self, pset1, pset2):
        self.assertTrue(len(pset1)==len(pset2))
        for pcon1 in pset1:
            for pcon2 in pset2:
                if pcon1.predicate==pcon2.predicate:
                    self.assertTrue(pcon1==pcon2)

    def test_Parser(self):
        parser = CoreConstraintParser()

        pconset = parser.parse("L <: L     ; (next_state=1)  =>  L <: next_state     ;  L <: next_state    ;")
        expects = [
            PCon("True", [Con(Label('L'), Op('<:'), Label('L')), Con(Label('L'), Op('<:'), CVar('next_state'))]),
            PCon("(next_state=1)", [Con(Label('L'), Op('<:'), CVar('next_state'))])
        ]
        self.check_same_pconset(pconset, expects)

        pconset = parser.parse('''True => L <: ax And az <: ax; d>0 => H <: ay; Not(d>0) => L <: ay; d>0 => H<: ay; d>0=> ay<:ax; True=>ax<:L''')
        expects = [
            PCon("True", [Con(Label('L'), Op('<:'), CVar('ax')), Con(CVar('az'), Op('<:'), CVar('ax')), Con(CVar('ax'), Op('<:'), Label('L'))]),
            PCon("d>0", [Con(Label('H'), Op('<:'), CVar('ay')),  Con(CVar('ay'), Op('<:'), CVar('ax'))]),
            PCon("Not(d>0)", [Con(Label('L'), Op('<:'), CVar('ay'))])
        ]
        self.check_same_pconset(pconset, expects)


if __name__ == '__main__':
    unittest.main(verbosity=2)




