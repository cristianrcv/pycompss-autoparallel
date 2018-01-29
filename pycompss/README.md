PyCOMPSs and PLUTO integration
=============================

PyCOMPSs and PLUTO integration using OpenSCOP.

## Table of Contents

* [Dependencies](#dependencies)
* [Disclaimer](#disclaimer)


## Dependencies

[COMPSs][1]: The COMP Superscalar (COMPSs) framework is mainly compose of a programming model which aims to ease the development of applications for distributed infrastructures, such as Clusters, Grids and Clouds and a runtime system that exploits the inherent parallelism of applications at execution time. The framework is complemented by a set of tools for facilitating the development, execution monitoring and post-mortem performance analysis. It natively supports Java but has bindings for Python, C and C++. 

[PLUTO][2]: PLUTO is an automatic parallelization tool based on the polyhedral model. The polyhedral model for compiler optimization provides an abstraction to perform high-level transformations such as loop-nest optimization and parallelization on affine loop nests. Pluto transforms C programs from source to source for coarse-grained parallelism and data locality simultaneously. The core transformation framework mainly works by finding affine transformations for efficient tiling. OpenMP parallel code for multicores can be automatically generated from sequential C program sections. Outer (communication-free), inner, or pipelined parallelization is achieved purely with OpenMP parallel for pragrams.

[OpenSCOP][3]: OpenScop is an open specification defining a file format and a set of data structures to represent a static control part (SCoP for short), i.e., a program part that can be represented in the polyhedral model. The goal of OpenScop is to provide a common interface to various polyhedral compilation tools in order to simplify their interaction. The OpenScop aim is to provide a stable, unified format that offers a durable guarantee that a tool can use an output or provide an input to another tool without breaking a tool chain because of some internal changes in one element of the chain. The other promise of OpenScop is the ability to assemble or replace the basic blocks of a polyhedral compilation framework at no, or at least low engineering cost.


### Test with debug

```
export PYTHONPATH=${git_base_dir}
python nose_tests.py
```


### Test without debug                                                                                                                                                                                                                                                         

```
export PYTHONPATH=${git_base_dir}
python -O nose_tests.py
```


### Clean

```
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```


### Run coverage

```
coverage run --omit="/usr/lib/*" nose_tests.py
coverage report -m
coverage xml
```


[1]: https://compss.bsc.es
[2]: http://pluto-compiler.sourceforge.net/
[3]: http://icps.u-strasbg.fr/people/bastoul/public_html/development/openscop/
[4]: https://www.inria.fr/en/teams/camus
[5]: https://www.inria.fr/
[6]: https://www.bsc.es/discover-bsc/organisation/scientific-structure/workflows-and-distributed-computing
[7]: https://www.bsc.es/

