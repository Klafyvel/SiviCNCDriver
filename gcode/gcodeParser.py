# Trace
# Copyright (C) 2015  Hugo LEVY-FALK
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class Pile:

    def __init__(self, in_str):
        self.in_str = in_str
        self.next = None

    def token(self):
        while len(self.in_str) > 0:
            yield self.pop()

    def pop(self):
        r = self.peek()
        self.next = None
        return r

    def peek(self):
        if not self.next:
            self.next = self.in_str[0]
            self.in_str = self.in_str[1:]
        return self.next

SEPARATOR = ('\n', ' ', '(', '=')


def parse(gcode):
    pile = Pile(gcode + '\n')
    for c in pile.token():
        if c is ' ':
            continue
        elif c is '(':
            com = ''
            while pile.peek() is not ')':
                com += pile.pop()
            pile.pop()  # removes the ')'
            yield ('__comment__', c)
        elif c is '\n':
            yield ('__next__', '__next__')
        elif c is '#':
            var_name = '#' + str(int(parse_value(pile).calc()))
            # wait for the '='
            while pile.peek() in SEPARATOR:
                pile.pop()
            var_value = parse_value(pile).calc()
            yield ('__new_var__', {var_name: var_value})
        else:
            yield (c, parse_value(pile))


def parse_instr(gcode):
    name = ""
    value = 0
    args = {}
    for i in parse(gcode):
        if not i[0] == '__next__':
            if i[0] == '__new_var__':
                name = ''
                value = None
                for a in i[1].keys():
                    OpNode.var[a] = i[1][a]
                    yield {'name': '__new_var__', 'var': a, 'value': i[1][a]}
                # TODO : manage variable declaration
            if i[0] in ('G', 'M'):
                name = i[0]
                value = i[1].calc()
            elif i[0] in 'XYZIJKN':
                args[i[0]] = i[1].calc()
            elif i[0] == '__comment__':
                if name is "":
                    name = 'comment'
                args['comments'] = i[1]
        elif name is not "":
            yield {'name': name, 'value': value, 'args': args}
            name = ""
            value = 0
            args = {}
    yield {'name': name, 'value': value, 'args': args}


def parse_value(pile):
    r = ''
    while pile.peek() not in SEPARATOR:
        if pile.peek() not in '[]':
            r += pile.pop()
        else:
            pile.pop()
    v = OpNode(r)
    return v


class OpNode:
    OP = {
        '+': lambda l, r: l.calc() + r.calc(),
        '-': lambda l, r: l.calc() - r.calc(),
        '*': lambda l, r: l.calc() * r.calc(),
        '/': lambda l, r: l.calc() / r.calc(),
        'Nop_var': lambda l, r: OpNode.var[l],
        'Nop_val': lambda l, r: float(l),
    }
    var = {}

    def __init__(self, input_str, print_this=False):
        p = input_str.split('+')
        m = input_str.split('-')
        d = input_str.split('/')
        t = input_str.split('*')

        if len(p) > 1:
            self.op_name = '+'
            self.op = self.OP['+']
            self.left = OpNode(p[0])
            self.right = OpNode('+'.join(p[1:]))
        elif len(m) > 1:
            self.op_name = '-'
            self.op = self.OP['-']
            if m[0] == '':  # i.e. a negative number
                self.left = OpNode('0')
            else:
                self.left = OpNode(m[0])
            self.right = OpNode('-'.join(m[1:]))
        elif len(t) > 1:
            self.op_name = '*'
            self.op = self.OP['*']
            self.left = OpNode(t[0])
            self.right = OpNode('*'.join(t[1:]))
        elif len(d) > 1:
            self.op_name = '/'
            self.op = self.OP['/']
            self.left = OpNode(d[0])
            self.right = OpNode('/'.join(d[1:]))
        else:
            self.op_name = 'Nop'
            try:
                float(input_str)
            except ValueError:
                self.op = self.OP['Nop_var']
            else:
                self.op = self.OP['Nop_val']
            self.left = input_str
            self.right = None
        if print_this:
            self.print()

    def calc(self):
        return self.op(self.left, self.right)

    def print(self, space_before=0):
        print(' ' * space_before + "->" + self.op_name, end="")
        if self.op_name is 'Nop':
            print(" = " + str(self.left))
        else:
            print()
            self.left.print(space_before + 1)
            print()
            self.right.print(space_before + 1)
            print()

# s = """G01 X-3.0 Y4
# N1 G02 Z3"""
if __name__ == '__main__':
    i = input()
    o = OpNode(i)
    print(o.calc())
