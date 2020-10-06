from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ReferenceVar(Generic[T]):
    """
    Creates a reference variable of any type.
    """
    def __init__(self, init: Optional[T] = None):
        self.value: Optional[T] = init

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        return str(self.value)

    def __len__(self):
        return len(self.value)