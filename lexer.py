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
                    print input_str[pos:]
                    raise UndefinedTokenError(input_str[pos:])
        return result


#  ------------------------- Lexer Tokens -----------------------
class NoneToken(Token):
    lex_reg = r'\s+'


class DebugToken(Token):
    lex_reg = r'\[ConsDebugTag-[0-9]*]'


class VariableToken(Token):
    lex_reg = r'[A-Za-z0-9_.,:!%*/()~{}$"\'&#<>+-]*'


class ConstToken(Token):
    lex_reg = r'CONST\[\S*\]\[\S*\]'


class FilenameToken(Token):
    lex_reg = r'[A-Za-z_][A-Za-z0-9_]*[.][A-Za-z0-9_]*'


# class ConVar(Token):
#     lex_reg = r'[a-z][A-Za-z0-9_]*'
#
#
# class LabelToken(Token):
#     lex_reg = r'[A-Z][A-Za-z0-9_]*'


class IntegerToken(Token):
    lex_reg = r'[0-9]*'


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


class SquareBracketStartToken(Token):
    lex_reg = r'\['


class SquareBracketEndToken(Token):
    lex_reg = r']'


class DelimToken(Token):
    lex_reg = r'\|'


class UndefinedTokenError(Exception):
    pass


def test_lexer(lexer, input_str):
    test_tokens = lexer.tokenize(input_str)
    for items in test_tokens:
        print items


if __name__ == '__main__':
    lexer = Lexer()
    lexer.add_tokens(NoneToken(), DebugToken(), ConstToken(),
                     SquareBracketStartToken(), SquareBracketEndToken(),
                     AndToken(), SubToken(),  DelimToken(),
                     SemiToken(),  VariableToken(), SatToken(), IntegerToken())

    # test_lexer(
    #     lexer, '''True => L <: ax And az <: ax; H <: ay; => L <: ay; True=>ax<:L''')
    # test_lexer(
    #     lexer, '''CE0x7f8a55c0c7e0[if.end7;Unknown_location;;] <: CE0x7f8a55c0c600[__ret_i32_0,_!dbg_!51;main.cpp;21;] ;  [ConsDebugTag-10]  main.cpp line 21''')
    test_lexer(
        lexer, '''CE0x7fbebf10a5f0[or|include/inner.h|627] <: CE0x7fbebf10a5b0[or|include/inner.h|627] ;  [ConsDebugTag-9]  include/inner.h line 627''')
    test_lexer(
        lexer, '''CE0x7faa3a412fa0[0:_struct.KeyS*,__8:_i32*,__:_HCME_0,8__||] <: CONST[source:1(mediator),value:0(dynamic)][purpose:{operation}] ''')
