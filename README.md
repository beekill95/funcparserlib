Funcparserlib
=============

Recursive descent parsing library for Python based on functional combinators.

[![PyPI](https://img.shields.io/pypi/v/funcparserlib)](https://pypi.org/project/funcparserlib/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/funcparserlib)](https://pypi.org/project/funcparserlib/)


Description
-----------

The primary domain of `funcparserlib` is **parsing little languages** or **external DSLs** (domain specific languages).

Parsers made with `funcparserlib` are pure-Python LL(\*) parsers. It means that it's **very easy to write parsers** without thinking about lookaheads and other hardcore parsing stuff. However, recursive descent parsing is a rather slow method compared to LL(k) or LR(k) algorithms. Still, parsing with `funcparserlib` is **at least twice as fast** as a very popular PyParsing library.

The source code of `funcparserlib` is only 1.2K lines of code, with lots of comments. Its API is fully type hinted. It features the longest parsed prefix error reporting, as well as a tiny lexer generator for token position tracking.

The idea of parser combinators used in `funcparserlib` comes from the [Introduction to Functional Programming](https://www.cl.cam.ac.uk/teaching/Lectures/funprog-jrh-1996/) course. We have converted it from ML into Python.


Installation
------------

You can install `funcparserlib` from [PyPI](https://pypi.org/project/funcparserlib/):

```shell
$ pip install funcparserlib
```

There are no dependencies on other libraries.


Documentation
-------------

* [Getting Started](https://funcparserlib.pirx.ru/getting-started/)
    * Your **starting point** with `funcparserlib`
* [API Reference](https://funcparserlib.pirx.ru/api/)
    * Learn the details of the API

There are several examples available in the `tests/` directory:

* [GraphViz DOT parser](https://github.com/vlasovskikh/funcparserlib/blob/master/tests/dot.py)
* [JSON parser](https://github.com/vlasovskikh/funcparserlib/blob/master/tests/json.py)

See also [the changelog](https://funcparserlib.pirx.ru/changes/).


Example
-------

Let's consider a little language of **numeric expressions** with a syntax similar to Python expressions. Here are some expression strings in this language:

```
0
1 + 2 + 3
-1 + 2 ** 32
3.1415926 * (2 + 7.18281828e-1) * 42
```


Here is **the complete source code** of the tokenizer and the parser for this language written using `funcparserlib`:

```python
from typing import List, Tuple, Union
from dataclasses import dataclass

from funcparserlib.lexer import make_tokenizer, TokenSpec, Token
from funcparserlib.parser import tok, Parser, many, forward_decl, finished


@dataclass
class BinaryExpr:
    op: str
    left: "Expr"
    right: "Expr"


Expr = Union[BinaryExpr, int, float]


def tokenize(s: str) -> List[Token]:
    specs = [
        TokenSpec("whitespace", r"\s+"),
        TokenSpec("float", r"[+\-]?\d+\.\d*([Ee][+\-]?\d+)*"),
        TokenSpec("int", r"[+\-]?\d+"),
        TokenSpec("op", r"(\*\*)|[+\-*/()]"),
    ]
    tokenizer = make_tokenizer(specs)
    return [t for t in tokenizer(s) if t.type != "whitespace"]


def parse(tokens: List[Token]) -> Expr:
    int_num = tok("int") >> int
    float_num = tok("float") >> float
    number = int_num | float_num

    expr: Parser[Token, Expr] = forward_decl()
    parenthesized = -op("(") + expr + -op(")")
    primary = number | parenthesized
    power = primary + many(op("**") + primary) >> to_expr
    term = power + many((op("*") | op("/")) + power) >> to_expr
    sum = term + many((op("+") | op("-")) + term) >> to_expr
    expr.define(sum)

    document = expr + -finished

    return document.parse(tokens)


def op(name: str) -> Parser[Token, str]:
    return tok("op", name)


def to_expr(args: Tuple[Expr, List[Tuple[str, Expr]]]) -> Expr:
    first, rest = args
    result = first
    for op, expr in rest:
        result = BinaryExpr(op, result, expr)
    return result
```

Let's tokenize an expression using the tokenizer we've created with `funcparserlib.lexer`:

```pycon
>>> pprint(tokenize("3.1415926 * (2 + 7.18281828e-1) * 42"))
[Token('float', '3.1415926'),
 Token('op', '*'),
 Token('op', '('),
 Token('int', '2'),
 Token('op', '+'),
 Token('float', '7.18281828e-1'),
 Token('op', ')'),
 Token('op', '*'),
 Token('int', '42')]

```

Let's parse these tokens into an expression tree using our parser created with `funcparserlib.parser`:

```pycon
>>> parse(tokenize("3.1415926 * (2 + 7.18281828e-1) * 42"))
BinaryExpr(op='*', left=BinaryExpr(op='*', left=3.1415926, right=BinaryExpr(op='+', left=2, right=0.718281828)), right=42)

```

Here is this tree in a pretty-printed form:

```pycon
>>> print(pretty_expr(document.parse(tokenize("3.1415926 * (2 + 7.18281828e-1) * 42"))))
BinaryExpr('*')
|-- BinaryExpr('*')
|   |-- 3.1415926
|   `-- BinaryExpr('+')
|       |-- 2
|       `-- 0.718281828
`-- 42

```

Learn how to write this parser using `funcparserlib` in the [Getting Started](https://funcparserlib.pirx.ru/getting-started/) guide!


Used By
-------

Some open-source projects that use `funcparserlib` as an explicit dependency:

* https://github.com/hylang/hy
    * 4.2K stars, version `>= 1.0.0a0`, Python 3.7+
* https://github.com/scrapinghub/splash
    * 3.6K stars, version `*`. Python 3 in Docker
* https://github.com/klen/graphite-beacon
    * 459 stars, version `==0.3.6`, Python 2 and 3
* https://github.com/blockdiag/blockdiag
    * 148 stars, version `>= 1.0.0a0`, Python 3.7+
* https://github.com/kiibohd/kll
    * 109 stars, copied source code, Python 3.5+
* https://gitlab.com/quantify-os/quantify-core
    * 19 stars, version `==1.0.0a0`, Python 3.8+


Similar Projects
----------------

* [LEPL](https://code.google.com/p/lepl/). A recursive descent parsing library that uses two-way generators for backtracking. Its source code is rather large: 17 KLOC.
* [pyparsing](https://github.com/pyparsing/pyparsing/). A recursive descent parsing library. Probably the most popular Python parsing library. Nevertheless, its source code is quite dirty (though 4 KLOC only).
