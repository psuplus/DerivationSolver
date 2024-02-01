from lexer import *
import copy

class Expr:
    def __init__(self, name, desc="", file="", line=""):
        self.name = name
        self.desc = desc
        self.file = file
        self.line = line

    def __eq__(self, other):
        return isinstance(other, Expr) and self.name == other.name

    def __str__(self):
        return self.name + '[' + self.desc + ']'


class Label(Expr):
    def __init__(self, name, desc="", file="", line=""):
        self.name = name
        self.desc = desc
        self.file = file
        self.line = line
        self.level = {}
        self.compartment = {}

    def __str__(self):
        return self.name+"_LABEL_"


class CVar(Expr):
    pass


class RLLabel(Label):
    def __init__(self, level={}, compartment={}):
        Label.__init__(self, "CONST")
        self.level = level
        self.compartment = compartment

    def __eq__(self, other):
        return isinstance(other, RLLabel) and self.level == other.level and self.compartment == other.compartment

    def __str__(self):
        return '[' + self.level.__str__() + '][' + self.compartment.__str__() + ']'

    def __hash__(self):
        return hash(self.__str__())

    def compare(self, other):
        if self == other:
            return 0
        else:
            gt = False
            lt = False
            for key in self.level:
                if self.level[key] > other.level[key]:
                    gt = True
                elif self.level[key] < other.level[key]:
                    lt = True
            for key in self.compartment:
                if len(self.compartment[key] - other.compartment[key]) > 0 and len(other.compartment[key] - self.compartment[key]) > 0:
                    gt = True
                    lt = True
                elif self.compartment[key] > other.compartment[key]:
                    gt = True
                elif self.compartment[key] < other.compartment[key]:
                    lt = True
            if gt and lt:
                return -2
            elif gt and (not lt):
                return 1
            elif (not gt) and lt:
                return -1
            else:
                raise Exception(
                    'This shouldn\'t happen, it should be dealt with in the previous branch')

    def parseConstString(self, str):
        re_match = (re.compile(r"CONST\[(.*)\]\[(.*)\]")).match(str)
        if re_match:
            level = re_match.group(1)
            compartment = re_match.group(2)
            level = re.split(',', level)
            for l in level:
                l_match = re.compile(r"([a-zA-Z0-9]*):([0-9]*)\(.*\)").match(l)
                self.level[l_match.group(1)] = int(l_match.group(2))
            compartment = re.compile(
                r"([a-zA-Z0-9]*:\{[a-zA-Z0-9,]*\})").findall(compartment)
            for c in compartment:
                c_match = re.compile(
                    r"([a-zA-Z0-9]*):\{([a-zA-Z0-9,]*)\}").match(c)
                self.compartment[c_match.group(1)] = set()
                if (c_match.group(2) == ''):
                    c_set = []
                else:
                    c_set = re.split(',', c_match.group(2))
                for e in c_set:
                    self.compartment[c_match.group(1)].add(e)
        else:
            raise Exception("Bad format!")


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


class PCon:
    def __init__(self, p, c):
        self.predicate = p
        self.constraints = c

    def __str__(self):
        return self.predicate + "=>" + pretty_conset_print(self.constraints)

    def __eq__(self, other):
        return isinstance(other, PCon) and self.__dict__ == other.__dict__


class CoreConstraintParser:
    def __init__(self, labels=["H", "L"]):
        self.lexer = Lexer()
        self.labels = labels
        self.init_lexer()

    def init_lexer(self):
        self.lexer.add_tokens(NoneToken(), DebugToken(), SquareBracketStartToken(), SquareBracketEndToken(),
                              AndToken(), SubToken(),  DelimToken(),
                              SemiToken(),  VariableToken(), SatToken(), IntegerToken())

    def generate_constraint(self, t_exp1, t_sub, t_exp2):
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

    def pre_process(self, input_str):
        return input_str

    def post_process(self, pconset):
        return pconset

    def generate_conset(self, input_str):
        conset = []
        cons = self.lexer.tokenize(input_str)
        has_sub = False
        for c in cons:
            if isinstance(c, SubToken):
                has_sub = True
        if not has_sub:
            return conset

        idx = 0
        consumed_exp1 = False
        while idx != len(cons):
            if (cons[idx].token_string in self.labels and (isinstance(cons[idx + 1], SubToken) or isinstance(cons[idx + 1], SemiToken))):
                if not consumed_exp1:
                    exp1 = Label('', cons[idx].token_string, '', '')
                    consumed_exp1 = True
                else:
                    exp2 = Label('', cons[idx].token_string, '', '')
                    constr = str(exp1) + '<:' + str(exp2)
                    conset.append(constr)
                    constr = ''
                    consumed_exp1 = False
                idx = idx + 1
            elif isinstance(cons[idx], VariableToken) and isinstance(cons[idx + 1], SquareBracketStartToken):
                addr = cons[idx].token_string
                name = file = line = ''
                idx = idx + 2
                if isinstance(cons[idx], VariableToken):
                    name = cons[idx].token_string
                    idx = idx + 1
                idx = idx + 1
                if isinstance(cons[idx], VariableToken):
                    file = cons[idx].token_string
                    idx = idx + 1
                idx = idx + 1
                if isinstance(cons[idx], VariableToken):
                    line = cons[idx].token_string
                    idx = idx + 1
                idx = idx + 1
                if not consumed_exp1:
                    exp1 = CVar(addr, name, file, line)
                    consumed_exp1 = True
                else:
                    exp2 = CVar(addr, name, file, line)
                    constr = str(exp1) + '<:' + str(exp2)
                    conset.append(constr)
                    constr = ''
                    consumed_exp1 = False
            elif isinstance(cons[idx], SubToken):
                idx = idx + 1
        return conset

    def generate_predicate(self, input_str):
        return input_str.strip()

    def parse(self, input_str):
        input_str = self.pre_process(input_str)

        constraints = [re.split(SatToken().lex_reg, c_tokens)
                       for c_tokens in re.split(SemiToken().lex_reg, input_str)]

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
                pconset.append(PCon(pred, copy.deepcopy(conset)))

        # merge the same predicate cases
        pconset_op = []
        predicates_dic = {}
        for pcon in pconset:
            if pcon.predicate in predicates_dic:
                predicates_dic[pcon.predicate] += pcon.constraints
            else:
                predicates_dic[pcon.predicate] = pcon.constraints
        for key in predicates_dic:
            pconset_op.append(PCon(key, predicates_dic[key]))

        return self.post_process(pconset_op)


def pretty_conset_print(conset):
    if conset:
        msg = "{"
        for cons in conset[:-1]:
            msg = msg + str(cons) + ", "
        msg = msg + str(conset[-1]) + "}"
        return msg
    else:
        return "{}"


def pretty_pcon_set_print(pconset):
    if pconset:
        msg = "{\n"
        for pcons in pconset[:-1]:
            msg = msg + "\t" + str(pcons) + "\n"
        msg = msg + "\t" + str(pconset[-1]) + "\n}"
        return msg
    else:
        return "{}"


def test_parser(parser, input_str):
    pconset = parser.parse(input_str)
    for pcons in pconset:
        print pcons


if __name__ == '__main__':

    parser = CoreConstraintParser()
    test_parser(
        parser, '''CE0x7fbebf10a5f0[or|include/inner.h|627] <: CE0x7fbebf10a5b0[or|include/inner.h|627] ;  [ConsDebugTag-9]  include/inner.h line 627''')
