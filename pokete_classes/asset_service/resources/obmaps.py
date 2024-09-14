# DO NOT EDIT!
# This code was auto generated by the `protoc-gen-pokete-resources` plugin,
# part of the pokete project, by <lxgr@protonmail.com>
from typing import TypedDict
from . import (Coords, CoordsDict, )


class DorArgsDict(TypedDict):
    x: int
    y: int
    map: str


class DorArgs:
    def __init__(
        self,
        x: int,
        y: int,
        map: str
    ):
        self.x: int = x
        self.y: int = y
        self.map: str = map

    @classmethod
    def from_dict(cls, _d: DorArgsDict | None) -> "DorArgs | None":
        if _d is None:
            return None
        return cls(
            x=_d["x"],
            y=_d["y"],
            map=_d["map"],
        )

    def to_dict(self) -> DorArgsDict:
        ret: DorArgsDict = {}
        
        ret["x"] = self.x
        ret["y"] = self.y
        ret["map"] = self.map
        
        return ret


class DorDict(TypedDict):
    x: int
    y: int
    args: "DorArgsDict"


class Dor:
    def __init__(
        self,
        x: int,
        y: int,
        args: "DorArgs"
    ):
        self.x: int = x
        self.y: int = y
        self.args: "DorArgs" = args

    @classmethod
    def from_dict(cls, _d: DorDict | None) -> "Dor | None":
        if _d is None:
            return None
        return cls(
            x=_d["x"],
            y=_d["y"],
            args=DorArgs.from_dict(_d["args"]),
        )

    def to_dict(self) -> DorDict:
        ret: DorDict = {}
        
        ret["x"] = self.x
        ret["y"] = self.y
        ret["args"] = DorArgs.to_dict(self.args)
        
        return ret


class SpecialDorsDict(TypedDict):
    dor: "CoordsDict | None"
    shopdor: "CoordsDict | None"


class SpecialDors:
    def __init__(
        self,
        dor: "Coords | None",
        shopdor: "Coords | None"
    ):
        self.dor: "Coords | None" = dor
        self.shopdor: "Coords | None" = shopdor

    @classmethod
    def from_dict(cls, _d: SpecialDorsDict | None) -> "SpecialDors | None":
        if _d is None:
            return None
        return cls(
            dor=Coords.from_dict(_d.get("dor", None)),
            shopdor=Coords.from_dict(_d.get("shopdor", None)),
        )

    def to_dict(self) -> SpecialDorsDict:
        ret: SpecialDorsDict = {}
        
        if self.dor is not None:
            ret["dor"] = Coords.to_dict(self.dor)
        if self.shopdor is not None:
            ret["shopdor"] = Coords.to_dict(self.shopdor)
        
        return ret


class ObDict(TypedDict):
    x: int
    y: int
    txt: str
    cls: str | None


class Ob:
    def __init__(
        self,
        x: int,
        y: int,
        txt: str,
        cls: str | None
    ):
        self.x: int = x
        self.y: int = y
        self.txt: str = txt
        self.cls: str | None = cls

    @classmethod
    def from_dict(cls, _d: ObDict | None) -> "Ob | None":
        if _d is None:
            return None
        return cls(
            x=_d["x"],
            y=_d["y"],
            txt=_d["txt"],
            cls=_d.get("cls", None),
        )

    def to_dict(self) -> ObDict:
        ret: ObDict = {}
        
        ret["x"] = self.x
        ret["y"] = self.y
        ret["txt"] = self.txt
        if self.cls is not None:
            ret["cls"] = self.cls
        
        return ret


class ObmapDict(TypedDict):
    hard_obs: dict[str, "ObDict"]
    soft_obs: dict[str, "ObDict"]
    dors: dict[str, "DorDict"]
    special_dors: "SpecialDorsDict | None"
    balls: dict[str, "CoordsDict"]


class Obmap:
    def __init__(
        self,
        hard_obs: dict[str, "Ob"],
        soft_obs: dict[str, "Ob"],
        dors: dict[str, "Dor"],
        special_dors: "SpecialDors | None",
        balls: dict[str, "Coords"]
    ):
        self.hard_obs: dict[str, "Ob"] = hard_obs
        self.soft_obs: dict[str, "Ob"] = soft_obs
        self.dors: dict[str, "Dor"] = dors
        self.special_dors: "SpecialDors | None" = special_dors
        self.balls: dict[str, "Coords"] = balls

    @classmethod
    def from_dict(cls, _d: ObmapDict | None) -> "Obmap | None":
        if _d is None:
            return None
        return cls(
            hard_obs={i: Ob.from_dict(item) for i, item in _d["hard_obs"].items()},
            soft_obs={i: Ob.from_dict(item) for i, item in _d["soft_obs"].items()},
            dors={i: Dor.from_dict(item) for i, item in _d["dors"].items()},
            special_dors=SpecialDors.from_dict(_d.get("special_dors", None)),
            balls={i: Coords.from_dict(item) for i, item in _d["balls"].items()},
        )

    def to_dict(self) -> ObmapDict:
        ret: ObmapDict = {}
        
        ret["hard_obs"] = {i: Ob.to_dict(item) for i, item in self.hard_obs.items()}
        ret["soft_obs"] = {i: Ob.to_dict(item) for i, item in self.soft_obs.items()}
        ret["dors"] = {i: Dor.to_dict(item) for i, item in self.dors.items()}
        if self.special_dors is not None:
            ret["special_dors"] = SpecialDors.to_dict(self.special_dors)
        ret["balls"] = {i: Coords.to_dict(item) for i, item in self.balls.items()}
        
        return ret
