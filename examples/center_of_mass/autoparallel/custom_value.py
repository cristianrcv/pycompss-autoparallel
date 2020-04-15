#!/usr/bin/python

# -*- coding: utf-8 -*-

class Value(object):

    def __init__(self, value=0):
        self.value = float(value)

    def __add__(self, other):
        return Value(self.value + other.value)

    def __iadd__(self, other):
        self.value += other.value
        return self

    def __div__(self, other):
        return Value(self.value / other.value) if other.value != float(0) else Value(0)

    def __idiv__(self, other):
        self.value /= other.value
        return self

    def __mul__(self, other):
        return Value(self.value * other.value)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __repr__(self):
        return "Value(" + str(self.value) + ")"

