#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.api.api import compss_barrier, compss_wait_on


@task(returns=list)
def create_block(b_size):
    import numpy as np

    block = np.array(np.random.random((b_size, b_size)), dtype=np.double, copy=False)
    mb = np.matrix(block, dtype=np.double, copy=False)

    return mb


@task(x=INOUT)
def update_block(x, y):
    x += y


if __name__ == "__main__":
    print("CREATE BLOCKS")
    a = create_block(4)
    b = create_block(4)

    print("WAIT FOR A BLOCK")
    a = compss_wait_on(a)
    print(a)

    print("UPDATE INOUT")
    update_block(a, b)

    print("WAIT FOR A BLOCK")
    a = compss_wait_on(a)
    print(a)
