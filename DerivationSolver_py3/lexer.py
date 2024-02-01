#!/usr/bin/env python3
# python >= 3.7

import logging
import unittest

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

    def __eq__(self, other):
        return self.__str__()==other.__str__();

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

class TestLexer(unittest.TestCase):
    def test_lexer(self):
        lexer = Lexer()
        lexer.add_tokens(NoneToken(), AndToken(), SubToken(), SemiToken(), VariableToken(), SatToken())
        test_tokens = lexer.tokenize('''True=> L   <: ax    And az <:   ax   ;
        
         H <: ay;  ''')
        expects = [
            VariableToken().new_token('True'),
            SatToken().new_token('=>'),
            VariableToken().new_token('L'),
            SubToken().new_token('<:'),
            VariableToken().new_token('ax'),
            AndToken().new_token('And'),
            VariableToken().new_token('az'),
            SubToken().new_token('<:'),
            VariableToken().new_token('ax'),
            SemiToken().new_token(';'),
            VariableToken().new_token('H'),
            SubToken().new_token('<:'),
            VariableToken().new_token('ay'),
            SemiToken().new_token(';'),
        ]
        self.assertTrue(len(test_tokens)==len(expects))
        for i in range(0, len(expects)):
            self.assertTrue(test_tokens[i]==expects[i])


if __name__ == '__main__':
    unittest.main(verbosity=2)




