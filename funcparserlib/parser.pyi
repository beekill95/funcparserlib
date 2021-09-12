from typing import (
    Optional,
    Generic,
    TypeVar,
    Union,
    Callable,
    Tuple,
    Sequence,
    Any,
    List,
    Text,
    overload,
)
from funcparserlib.lexer import Token

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")

class State:
    pos: int
    max: int
    parser: Union[Parser, _ParserCallable, None]
    def __init__(
        self,
        pos: int,
        max: int,
        parser: Union[Parser, _ParserCallable, None] = ...,
    ) -> None: ...

_ParserCallable = Callable[[_A, State], Tuple[_B, State]]

class Parser(Generic[_A, _B]):
    name: Text
    def __init__(self, p: Union[Parser[_A, _B], _ParserCallable]) -> None: ...
    def named(self, name: Text) -> Parser[_A, _B]: ...
    def define(self, p: Union[Parser[_A, _B], _ParserCallable]) -> None: ...
    def run(self, tokens: Sequence[_A], s: State) -> Tuple[_B, State]: ...
    def parse(self, tokens: Sequence[_A]) -> _B: ...
    @overload
    def __add__(  # type: ignore[misc]
        self, other: _IgnoredParser[_A]
    ) -> Parser[_A, _B]: ...
    @overload
    def __add__(self, other: Parser[_A, _C]) -> _TupleParser[_A, Tuple[_B, _C]]: ...
    def __or__(self, other: Parser[_A, _C]) -> Parser[_A, Union[_B, _C]]: ...
    def __rshift__(self, f: Callable[[_B], _C]) -> Parser[_A, _C]: ...
    def bind(self, f: Callable[[_B], Parser[_A, _C]]) -> Parser[_A, _C]: ...
    def __neg__(self) -> _IgnoredParser[_A]: ...

class _Ignored:
    value: Any
    def __init__(self, value: Any) -> None: ...

class _IgnoredParser(Parser[_A, _Ignored]):
    @overload  # type: ignore[override]
    def __add__(self, other: _IgnoredParser[_A]) -> _IgnoredParser[_A]: ...
    @overload  # type: ignore[override]
    def __add__(self, other: Parser[_A, _C]) -> Parser[_A, _C]: ...

class _TupleParser(Parser[_A, _B]):
    @overload  # type: ignore[override]
    def __add__(self, other: _IgnoredParser[_A]) -> _TupleParser[_A, _B]: ...
    @overload
    def __add__(self, other: Parser[_A, Any]) -> Parser[_A, Any]: ...

finished: Parser[Any, None]

def many(p: Parser[_A, _B]) -> Parser[_A, List[_B]]: ...
def some(pred: Callable[[_A], bool]) -> Parser[_A, _A]: ...
def a(value: _A) -> Parser[_A, _A]: ...
def tok(type: Text, value: Optional[Text] = ...) -> Parser[Token, Text]: ...
def pure(x: _A) -> Parser[_A, _A]: ...
def maybe(p: Parser[_A, _B]) -> Parser[_A, Optional[_B]]: ...
def skip(p: Parser[_A, _B]) -> _IgnoredParser[_A]: ...
def oneplus(p: Parser[_A, _B]) -> Parser[_A, List[_B]]: ...
def forward_decl() -> Parser[Any, Any]: ...

class NoParseError(Exception):
    msg: Text
    state: State
    def __init__(
        self, msg: Optional[Text] = ..., state: Optional[State] = ...
    ) -> None: ...
