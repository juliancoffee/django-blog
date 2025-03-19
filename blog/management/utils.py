from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

R = TypeVar("R")
E = TypeVar("E")


@dataclass
class Result(Generic[R, E]):
    # Poor's man tagged unions
    #
    # I suspect there are ways to implement this in a cleaner way, but it's a
    # rough sketch.
    # For example I'm sure there a ways to use TypeIs or TypeGuard somewhere to
    # make it more convenient to use.
    #
    # It this monadic horror required? Well, probably not, but it makes my life
    # eaiser.
    #
    # P. S. `dry-python/returns` exists, but my Result is walk in the park in
    # comparison.
    # Random package named `poltergeist` or `rustedpy/result` looks prettier,
    # but both aren't actively maintained. Not like it needs a lot of work
    # though, the interface is pretty defined and implementation is simple.
    #
    # In any case, this pattern isn't really popular in python world :(

    _res: R | E
    _state: Literal["OK", "ERR"]

    @staticmethod
    def ok(val: R) -> Result[R, E]:
        return Result(_res=val, _state="OK")

    @staticmethod
    def err(val: E) -> Result[R, E]:
        return Result(_res=val, _state="ERR")

    def get(self) -> Ok[R] | Err[E]:
        if self._state == "OK":
            return Ok(_val=cast("R", self._res))
        else:
            return Err(_val=cast("E", self._res))

    def is_ok(self) -> bool:
        return self._state == "OK"

    def is_err(self) -> bool:
        return not self.is_ok()

    def ok_or_none(self) -> R | None:
        if self.is_ok():
            return cast("R", self._res)
        else:
            return None

    def err_or_none(self) -> E | None:
        if self.is_err():
            return cast("E", self._res)
        else:
            return None

    def ok_or_raise(self) -> R:
        x = self.ok_or_none()
        if x is None:
            raise ValueError("unexpected error: {self._res}")
        return x

    def err_or_raise(self) -> E:
        x = self.err_or_none()
        if x is None:
            raise ValueError("unexpected ok: {self._res}")
        return x


@dataclass
class Ok(Generic[R]):
    __match_args__ = ("_val",)

    _val: R


@dataclass
class Err(Generic[E]):
    __match_args__ = ("_val",)

    _val: E
