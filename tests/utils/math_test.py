import pytest
from src.utils import math

def test_add_positive():
    assert math.add(1, 2) == 3

def test_add_negative():
    assert math.add(-1, -2) == -3

def test_add_zero():
    assert math.add(0, 0) == 0
    assert math.add(5, 0) == 5
