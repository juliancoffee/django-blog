from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

R = TypeVar("R")
E = TypeVar("E")


@dataclass
class Result(Generic[R, E]):
    # Poor's man tagged unions
    #
    # It this monadic horror required? Well, probably not.
    # It kind of makes my life easier though.
    # At the very least, it gives you a way to document exception without
    # giving up on typechecking.
    #
    # In any case, this pattern isn't really popular in python world, but
    # let me have my little experiment on a solo project.

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
            if isinstance(self._res, Exception):
                raise self._res
            else:
                raise ValueError(f"unexpected error: {self._res}")
        return x

    def err_or_raise(self) -> E:
        x = self.err_or_none()
        if x is None:
            raise ValueError(f"unexpected ok: {self._res}")
        return x


@dataclass
class Ok(Generic[R]):
    __match_args__ = ("_val",)

    _val: R


@dataclass
class Err(Generic[E]):
    __match_args__ = ("_val",)

    _val: E
