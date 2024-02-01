from solver import PartitionDerivationSolver
from parser import *
from z3supp import Z3Supp
import globals
import sys
import os

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