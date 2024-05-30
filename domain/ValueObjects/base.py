from abc import ABC
from dataclasses import dataclass

from typing import Any, Generic, TypeVar

V = TypeVar('V', bound=Any)


@dataclass(frozen=True)
class ValueObject(ABC, Generic[V]):
	"""ValueObject"""
	 
	_value: V

	def __post_init__(self) -> None:
		self._validate()

	def _validate(self) -> None:
		"""This method checks that a value is valid to create this value object"""
		pass

	def raw(self) -> V:
		return self._value