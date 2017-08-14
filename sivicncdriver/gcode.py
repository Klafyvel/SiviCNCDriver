"""
A module to parse G-codes.
"""

from sivicncdriver.settings import logger

__all__ = ['parse']

class Stack:
    """
    A Simple LIFO.
    """

    def __init__(self, in_str):
        """
        __init__ method.

        :param in_str: The string which is to be stacked.
        :type in_str: str
        """
        self.in_str = in_str
        self.next = None

    def __str__(self):
        return self.in_str

    def token(self):
        """
        Yields the elements of the stack.
        """
        while len(self.in_str) > 0:
            yield self.pop()

    def pop(self):
        """
        Pop an element.

        :return: The first element of the string.
        :rtype: str
        """
        r = self.peek()
        self.next = None
        return r

    def peek(self):
        """
        Peek the next element to be popped without popping it.

        :return: The next element
        :rtype: str
        """
        if not self.next:
            self.next = self.in_str[0]
            self.in_str = self.in_str[1:]
        return self.next

    def is_empty(self):
        """
        Returns True if the stack is empty.
        """
        return len(self.in_str) <= 0

SEPARATOR = ('\n', ' ', '(', '=')


def parse_iterator(gcode):
    """
    Function used by the ``parse`` function.

    :param gcode: The gcode which is to be parsed.
    :type gcode: str
    """
    stack = Stack(gcode + '\n')
    line = 0
    for c in stack.token():
        if c in ' %':
            continue
        elif c is '(':
            com = ''
            while stack.peek() is not ')':
                com += stack.pop()
            stack.pop()  # removes the ')'
            yield ('__comment__', com, line)
        elif c is '\n':
            yield ('__next__', '__next__', line)
            line += 1
        else:
            try:
                yield (c, parse_value(stack), line)
            except ValueError:
                yield ('__error__', c, line)


def parse(gcode):
    """ 
    Parse gcode.

    It yields a dict for each line with :

    name
        name of the code (G, M)
    value
        an integer
    args
        a dict with the code arguments, ex : {'Y':3.0}

    :param gcode: The gcode which is to be parsed.
    :type gcode: str
    """
    name = ""
    value = 0
    args = {}
    for i in parse_iterator(gcode):
        if i[0] == '__error__':
            yield {'name' : '__error__', 'line':i[2], 'value':i[1]}
        elif not i[0] == '__next__':
            if i[0] == '__new_var__':
                name = ''
                value = None
                for a in i[1].keys():
                    OpNode.var[a] = i[1][a]
                    yield {'name': '__new_var__', 'var': a, 'value': i[1][a], 'line':i[2]}
            if i[0] in ('G', 'M'):
                name = i[0]
                value = i[1]
            elif i[0] in 'XYZIJKN':
                args[i[0]] = i[1]
            elif i[0] == '__comment__':
                if name is "":
                    name = 'comment'
                args['comment'] = i[1]
        elif name is not "":
            yield {'name': name, 'value': value, 'args': args, 'line':i[2]}
            name = ""
            value = 0
            args = {}
    yield {'name': name, 'value': value, 'args': args, 'line':i[2]}


def parse_value(stack):
    """
    Parse a value in the stack.
    :param stack: The parser's stack.
    :return: The value.
    """
    r = ''
    while (not stack.is_empty()) and ((stack.peek() not in SEPARATOR) or (not r)):
        r += stack.pop()
    return float(r)
