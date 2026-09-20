"""Common interface for agent tools."""

from __future__ import annotations


class BaseTool:
    name: str = ""
    description: str = ""

    def run(self, **kwargs):
        raise NotImplementedError