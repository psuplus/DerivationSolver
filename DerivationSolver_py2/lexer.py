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
import re


class Token:
    lex_reg = ""

    def __init__(self):
        self.token_string = ""

    def new_token(self, token_str):
        token = self.__class__()
        token.token_string = token_str
        return token

    def __str__(self):
        return "(" + self.__class__.__name__ + ", " + self.token_string + ")"


class Lexer:
    def __init__(self):
        self.terminals = []

    def add_tokens(self, *terms):
        for term in terms:
            assert isinstance(term, Token)
            self.terminals.append(term)

    def tokenize(self, input_str):
        result = []
        pos = 0
        escape = NoneToken()
        while pos < len(input_str):
            token = (re.compile(escape.lex_reg)).match(input_str, pos)
            if token:
                pos = token.end(0)
            else:
                for terms in self.terminals:
                    token = (re.compile(terms.lex_reg)).match(input_str, pos)
                    if token:
                        result.append(terms.new_token(token.group(0)))
                        pos = token.end(0)
                        break
                if not token:
                    raise UndefinedTokenError(input_str[pos:])
        return result


#  ------------------------- Lexer Tokens -----------------------
class NoneToken(Token):
    lex_reg = r'\s+'


class VariableToken(Token):
    lex_reg = r'[A-Za-z_][A-Za-z0-9_]*'


# class ConVar(Token):
#     lex_reg = r'[a-z][A-Za-z0-9_]*'
#
#
# class LabelToken(Token):
#     lex_reg = r'[A-Z][A-Za-z0-9_]*'

#
class AndToken(Token):
    lex_reg = r'And'


class OrToken(Token):
    lex_reg = r'Or'


class NotToken(Token):
    lex_reg = r'Not'


class TrueToken(Token):
    lex_reg = r'True'


class FalseToken(Token):
    lex_reg = r'False'


class SatToken(Token):
    lex_reg = r'=>'


class SubToken(Token):
    lex_reg = r'<:'


class SemiToken(Token):
    lex_reg = r';'


class UndefinedTokenError(Exception):
    pass


def test_lexer(lexer, input_str):
    test_tokens = lexer.tokenize(input_str)
    for items in test_tokens:
        print items


if __name__ == '__main__':
    lexer = Lexer()
    lexer.add_tokens(NoneToken(), AndToken(), SubToken(), SemiToken(), VariableToken(), SatToken())

    test_lexer(lexer, '''True => L <: ax And az <: ax; H <: ay; => L <: ay; True=>ax<:L''')




