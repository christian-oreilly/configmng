import typing


class NotMergeable(Exception):
    def __init__(self, message: str):
        self.message = message


class MatchingRuleViolation(Exception):
    def __init__(self, message: str):
        self.message = message


class UndefinedScalarMerging(Exception):
    def __init__(self, keys: typing.Iterable):
        self.keys = keys


class UndefinedSequenceMerging(Exception):
    def __init__(self, keys: typing.Iterable):
        self.keys = keys


class MappingNonMappingMerging(Exception):
    def __init__(self, keys: typing.Iterable):
        self.keys = keys
