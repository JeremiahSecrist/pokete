# DO NOT EDIT!
# This code was auto generated by the `protoc-gen-pokete-resources-python` plugin,
# part of the pokete project, by <lxgr@protonmail.com>
from typing import TypedDict


class TypeDict(TypedDict):
    effective: list[str]
    ineffective: list[str]
    color: list[str]


class Type:
    def __init__(
        self,
        effective: list[str],
        ineffective: list[str],
        color: list[str]
    ):
        self.effective: list[str] = effective
        self.ineffective: list[str] = ineffective
        self.color: list[str] = color

    @classmethod
    def from_dict(cls, _d: TypeDict | None) -> "Type | None":
        if _d is None:
            return None
        return cls(
            effective=_d["effective"],
            ineffective=_d["ineffective"],
            color=_d["color"],
        )

    @staticmethod
    def validate(_d: TypeDict) -> bool:
        return all([
            "effective" in _d and all(type(i) is str for i in _d["effective"]),
            "ineffective" in _d and all(type(i) is str for i in _d["ineffective"]),
            "color" in _d and all(type(i) is str for i in _d["color"]),
        ])

    def to_dict(self) -> TypeDict:
        ret: TypeDict = {}
        
        ret["effective"] = self.effective
        ret["ineffective"] = self.ineffective
        ret["color"] = self.color

        return ret
