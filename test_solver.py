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
from solver import *
#from plot import *
from result import *
from parser import *
import globals
import sys
import os

TEST_DIR = "tests/"


class CommentToken(Token):
    lex_reg = r';.*\n'


class JoinToken(Token):
    lex_reg = r'[jJ]oin'


class ParenLeftToken(Token):
    lex_reg = r'\('


class ParenRightToken(Token):
    lex_reg = r'\)'


class LeftJoinParser(CoreConstraintParser):
    def __init__(self, labels=["H", "L"]):
        CoreConstraintParser.__init__(self, labels)
        self.z3 = Z3Supp()

    def __extract_predicates(self, input_str):
        result = []
        start = 0
        deep = 0
        index = 0
        if input_str == "True":
            return ["True"]

        for char in input_str:
            if char == '(':
                if deep == 0:
                    start = index
                deep += 1
            elif char == ')':
                if deep == 1:
                    result.append(input_str[start+1:index])
                if deep > 0:
                    deep -= 1
            index += 1
        return result

    def init_lexer(self):
        self.lexer.add_tokens(NoneToken(), ParenLeftToken(), ParenRightToken(), JoinToken(),
                              AndToken(), SubToken(), SemiToken(), VariableToken())

    def pre_process(self, input_str):
        return re.sub(CommentToken().lex_reg, ';', input_str)

    def post_process(self, pconset):
        result = []
        for pcon in pconset:
            # ignore invalid predicates
            if not self.z3.valid_p(pcon.predicate):
                continue
            conset = []
            # ignore left L and right H
            for con in pcon.constraints:
                if con.left.name != "L" and con.right.name != "H":
                    conset.append(con)
            if conset:
                pcon.constraints = conset
                result.append(pcon)
        return result

    def generate_predicate(self, input_str):
        input_str = input_str.strip()
        preds = self.__extract_predicates(input_str)
        return self.z3.and_predicates(*preds)

    def generate_conset(self, input_str):
        cons = self.lexer.tokenize(input_str)
        conset = []
        state = 0
        left = []
        sub_token = SubToken()
        for token in cons:
            if isinstance(token, VariableToken):
                if state == 0:
                    left.append(token)
                else:
                    for var in left:
                        conset.append(self.generate_constraint(var, sub_token, token))
                    left = []
            elif isinstance(token, SubToken):
                state = 1
                sub_token = token
            elif isinstance(token, AndToken):
                state = 0
        return conset


class TestSolver(PartitionDerivationSolver):
    def __init__(self, partt=SequentialPartition()):
        PartitionDerivationSolver.__init__(self, partt)

    def pretty_solution(self):
        msg = " {\n"
        for predicate in self.solution:
            msg += "\t" + predicate + " => {"
            empty = 0
            for var in self.solution[predicate]:
                if (self.solution[predicate])[var].name == "H":
                    msg += var + ", "
                    empty = 1
            if empty == 1:
                msg = msg[:-2]
            msg += "}\n"
        msg += "}"
        return msg


def test_file(file_name, partts, appr):
    if file_name[len(con_ext)*-1:] == con_ext:
        print ("Working on file: " + file_name)
        test_file = open(file_name, 'r')
        input_str = test_file.read()
        test_file.close()

        pconset = LeftJoinParser().parse(input_str)
        num = len(pconset)
        if globals.DEBUG:
            print(len(pretty_pcon_set_print(pconset)))
            print ("Constraint Set: \n" + pretty_pcon_set_print(pconset))
            print ("#predicates: " + str(num))
            #print "#predicates: " + str(pconset)

        cur_perform = {}
        for i in globals.Approach.keys():
            cur_perform[i] = []

        for partt in partts:
            solver = TestSolver()
            if partt == globals.COMB_PARTT:
                solver = TestSolver(CombinationPartition())
            # elif partt == globals.OP_COMB_PARTT:
            #     solver = TestSolver(OpCombinationPartition())

            files.append(file_name[len(TEST_DIR):len(con_ext)*-1])
            number.append(num)
            partt_alg.append(partt)
            for i in globals.Approach:
                if i in appr:
                    solver.solve_constraint(pconset, i)
                    cur_perform[i].append(solver.time)
                    perform[i].append(solver.time)
                else:
                    cur_perform[i].append(0)
                    perform[i].append(0)

        # plot_bar_chart(RESULT_DIR+file_name[len(TEST_DIR):]+plt_ext, partts, cur_perform)
        # files += cur_files
        # number += cur_number


files = []
number = []
partt_alg = []
perform = {}
for i in globals.Approach.keys():
    perform[i] = []

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print ("Usage: test_solver.py [test_file] -op [op]")
        print ("\t [test_file]: test file .con; use \'all\' to run all the file under tests/")
        print ("\t -partt [0-1]: -partt [0-1]: specifying partition algorithm: 0=sequential,")
        print ("\t\t\t1=combinational; if not specified, it tests all the partt ")
        print ("\t\t\talgorithms")
        print ("\t -appr [0-3]: specifying approaches: 0=hybrid, 1=early-accept, 2=one-shot,")
        print ("\t\t\t3=early-reject; if not specified, it tests [0,1,2] approaches.")
        print ("\t -time  i : specifying time-out minutes; default i=3 min.")
        print ("\t -debug [0-1] : print debug message; default 1 with debug message on")

    else:
        file_name = output_file_name("Test_file")
        # print file_name
        # try:
        partt = globals.ParttAlg.keys()
        appr = globals.Approach.keys()
        #appr.pop(globals.EARLY_REJECT_APPROACH)
        #appr.pop(globals.EARLY_REJECT_APPROACH)
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "-partt":
                partt = [int(sys.argv[i+1])]
                print (partt)
            elif sys.argv[i] == "-appr":
                appr = [int(sys.argv[i+1])]
            elif sys.argv[i] == "-time":
                globals.STOP_MIN = float(sys.argv[i+1])
            elif sys.argv[i] == "-debug":
                globals.DEBUG = int(sys.argv[i+1])

        file_test = sys.argv[1]
        if sys.argv[1] == 'all':
            file_test = [TEST_DIR + file for file in os.listdir(TEST_DIR)]
            for test_file_name in file_test:
                test_file(test_file_name, partt, appr)
        else:
            test_file(file_test, partt, appr)

        # save result:
        if files:
            store_result_file(file_name, files, number, partt_alg, perform)

        # if sys.argv[1] == 'all':
        #     plot_line_chart(file_name + plt_ext, partt, appr, number, partt_alg, perform)
