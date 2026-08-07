"""Day 4: Assembler's intentionally small public API.

Concept: export the composition class and extension primitives from one place.
Design rules: keep imports explicit and expose only the stable teaching surface.
"""

from .harness import Harness
from .security import Policy
from .tools import Tool, tool

__all__ = ["Harness", "Policy", "Tool", "tool"]
