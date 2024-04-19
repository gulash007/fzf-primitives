from string import Template
from typing import Any, Iterable, TypeVar

T = TypeVar("T")


class ParametrizedOptionString:
    def __init__(self, template: str, placeholders_to_resolve: Iterable[str] = ()) -> None:
        """
        Args:
            template (str): Should contain placeholders in the format: $some_placeholder (same as bash variable)
            placeholders_to_resolve (Iterable[str], optional): An iterable of placeholders that are required
            to be resolved before this object is used in a fzf option.
            Defaults to ().
        """
        self.template = template
        self.placeholders_to_resolve = set(placeholders_to_resolve)
        self.resolved_placeholders: dict[str, Any] = {}

    @property
    def resolved(self) -> bool:
        return set(self.resolved_placeholders) == self.placeholders_to_resolve

    def resolve(self, **mapping):
        for key, value in mapping.items():
            if key not in self.placeholders_to_resolve:
                raise RuntimeError(f"{self}: {key} not in {self.placeholders_to_resolve=}")
            if key in self.resolved_placeholders:
                raise RuntimeError(f"{self}: {key} already resolved")
            self.resolved_placeholders.update({key: value})

    def resolved_string(self) -> str:
        """To resolve into action string that can be used in --bind '<event>:<action string>'"""
        if not self.resolved:
            raise NotResolved(
                f"{self}: Not resolved {self.placeholders_to_resolve.difference(self.resolved_placeholders)}"
            )
        return Template(self.template).safe_substitute(self.resolved_placeholders)

    def __str__(self) -> str:
        return f"'{self.template}' ({self.placeholders_to_resolve=}) ({self.resolved_placeholders=})"


class NotResolved(RuntimeError): ...
