from __future__ import annotations


class Registry[K, V]:
    def __init__(self) -> None:
        self._items: dict[K, V] = {}
        self._frozen: bool = False

    def register(self, key: K, value: V) -> None:
        if self._frozen:
            err_msg = f"{type(self).__name__} is frozen; cannot register {key!r}"
            raise RuntimeError(err_msg)
        if key in self._items:
            err_msg = f"{key!r} already registered in {type(self).__name__}"
            raise ValueError(err_msg)
        self._items[key] = value

    def get(self, key: K) -> V | None:
        return self._items.get(key)

    def __contains__(self, key: K) -> bool:
        return key in self._items

    def freeze(self) -> None:
        self._frozen = True

    @property
    def keys(self) -> set[K]:
        return set(self._items.keys())


class FanOutRegistry[K, V]:
    def __init__(self) -> None:
        self._items: dict[K, list[V]] = {}
        self._frozen: bool = False

    def register(self, key: K, value: V) -> None:
        if self._frozen:
            err_msg = f"{type(self).__name__} is frozen; cannot register {key!r}"
            raise RuntimeError(err_msg)
        self._items.setdefault(key, []).append(value)

    def get(self, key: K) -> list[V]:
        return list(self._items.get(key, []))

    def __contains__(self, key: K) -> bool:
        return key in self._items

    def freeze(self) -> None:
        self._frozen = True

    @property
    def keys(self) -> set[K]:
        return set(self._items.keys())
