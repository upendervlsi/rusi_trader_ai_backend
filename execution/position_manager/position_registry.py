"""
============================================================

Position Registry

============================================================
"""

from execution.position_manager.position import Position


class PositionRegistry:

    def __init__(self):

        self._positions = {}

    def add(self, position: Position):

        self._positions[position.position_id] = position

    def get(self, position_id):

        return self._positions.get(position_id)

    def all(self):

        return list(self._positions.values())

    def open_positions(self):

        return [

            position

            for position in self._positions.values()

            if position.status.name == "OPEN"
        ]
