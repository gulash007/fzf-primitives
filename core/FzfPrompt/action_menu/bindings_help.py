from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ActionMenu import ActionMenu


def get_bindings_help(action_menu: ActionMenu) -> str:
    return "\n".join(f"{event}\t{binding.name}" for event, binding in action_menu.bindings.items())
