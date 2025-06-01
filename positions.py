#positions.py
import time
import asyncio
from datetime import datetime, timezone

class Position:
    def __init__(self, symbol, direction, entry_price, targets, stop_loss):
        # existing attributes...
        self.confirmed = False  # New: track if user confirmed position
        self.symbol = symbol
        self.direction = direction  # "LONG" or "SHORT"
        self.entry_price = entry_price
        self.targets = targets  # list of price targets (floats)
        self.stop_loss = stop_loss
        self.open_time = datetime.now(timezone.utc)  # Timezone-aware UTC datetime
        self.last_reported_target = None
        self.closed = False
        self.close_price = None
        self.close_time = None
        self.message = None  # Discord message object (for editing)
        self.last_reported_gain = 0.0  # no __init__


    def check_targets(self, current_price):
        """
        Check which target has been hit based on direction and price.
        Returns target price hit or None.
        """
        if self.closed:
            return None

        for target in self.targets:
            if self.last_reported_target is None or target > self.last_reported_target:
                if self.direction == "LONG" and current_price >= target:
                    return target
                if self.direction == "SHORT" and current_price <= target:
                    return target
        return None

    def check_stop_loss(self, current_price):
        """
        Check if stop loss was hit.
        """
        if self.closed:
            return False
        if self.direction == "LONG" and current_price <= self.stop_loss:
            return True
        if self.direction == "SHORT" and current_price >= self.stop_loss:
            return True
        return False

    def close(self, price):
        self.closed = True
        self.close_price = price
        self.close_time = datetime.now(timezone.utc)  # Timezone-aware UTC datetime

class PositionManager:
    def __init__(self):
        self.positions = {}

    def add_position(self, position: Position):
        self.positions[position.symbol] = position

    def remove_position(self, symbol):
        if symbol in self.positions:
            del self.positions[symbol]

    def get_positions(self):
        return list(self.positions.values())

    def get_position(self, symbol):
        return self.positions.get(symbol, None)
