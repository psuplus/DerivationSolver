# Derivation Solver 


## License Notice
****************************
Derivation Solver provides implementation of derivation solvers for dependent 
type inference. It consists of four constraint solvers, i.e., one-shot, 
early-accept, early-reject and hybrid solver along with two partition 
algorithms: sequential and combinational partitioning. A parser for the core 
constraint language and plotting scripts are also available in the package.

Copyright (C) 2018  Peixuan Li

Derivation Solver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Derivation Solver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.



## Dependency
****************************

The solvers are implemented in Python with external support from Z3.  Our 
evaluation is set up using Python 2.7.10 and Z3 4.5.0, but the implementation 
is not specialized to these versions. It is expected to be compatible for most 
of the existing version of Python and Z3. After evaluation data are 
obtained, we use gnuplot to visualize the result. 
In summary, here is the list of dependency:

- python (https://www.python.org/)
- Z3 (https://github.com/Z3Prover/z3)
- gnuplot (http://www.gnuplot.info/)


** Note that Z3 needs to be installed and be binded to the python in use. Here 
is a quick test to verify the binding:
1. launch python in the command line:
$ python
2. In the python console, type :
>>> from z3 import *
>>> x = Real('x')

If both statements finished with no error message, then Z3 is successfully 
binded; otherwise, either Z3 is not successfully installed or not binding with 
the python in use. Please refer to the Z3 binding 
(https://github.com/Z3Prover/z3) for more details. 


## Quick Taste
****************************

Here is a quick demo to run a small test case(dsram.con). By default, the 
 test will solve the constraints in tests/dsram.con using all three 
different solvers across two partition algorithms(6 unit tests in total):

$ python test_solver.py tests/dsram.con


Debug message will be printing out during the execution and the execution time 
is saved under the result folder with name in form of 
'[test file name]+[arguments]+[timestamps].csv'. 
Thus, you should find a result file "dsramXXXXXXXX.csv" in result folder when 
the it is complete. The file contains the execution time for all 6 test cases. 



## Reproducing the evaluation result
****************************

To reproduce the evaluation result reported in the paper, here are the steps:
1. run all the test files with three solvers(no early-reject since most of the 
test cases are solvable and early-reject solver is not useful for solvable 
cases) across two partition algorithms:

$ python test_solver.py all

This could take hours(~8h in our case) to finish. A brief break-down:
100 test file * 3 approaches * 2 partition algorithms = 600 unit test cases.

When it is done, a performance file "all[timestamp].csv" should be produced 
under result/ folder. We include our previous result file 
"all-time_3333_13_21_34.csv" in the folder. We use this 
file as example for the next steps.

2. plot the performance graph[Fig 9] using the result file. The file 
performance graph, named "performance-file.pdf" should be produced 
under result\ folder.

$ gnuplot -c plot-filewise.gnu result/all-time_3333_13_21_34.csv


3. plot the scalability graph[Fig 10] using the result file. The scalability 
graph, named "scalability.pdf" should be produced under result\ folder.

$ gnuplot -c plot-scalability.gnu result/all-time_3333_13_21_34.csv

4. plot the sequential vs combination graph[Fig 11] using the result file. The 
comparison graph, named "seq-comb.pdf" should be produced under result\ folder.

$ gnuplot -c plot-seq-comb.gnu result/all-time_3333_13_21_34.csv



## Reuse 
****************************

The current implementation provides multiple levels of reuse for future needs.

- Tuning running parameters.
The complete usage of the code is as follow:
Usage: test_solver.py [test_file] -op [op]
	 [test_file]: test file .con; use 'all' to run all the file under tests/
	 -partt [0-1]: specifying partition algorithm: 0=sequential, 
				   1=combinational; if not specified, it tests all the partt 
				   algorithms
	 -appr [0-3]: specifying approaches: 0=hybrid, 1=early-accept, 2=one-shot,
				 3=early-reject; if not specified, it tests [0,1,2] approaches.
	 -time  i : specifying time-out minutes; default i=3 min.
	 -debug [0-1] : print debug message; default 1 with debug message on.

Example 1: run tests/dsram.con using hybrid solver with sequential partitioning:
$ python test_solver.py tests/dsram.con -partt 0 -appr 0

Example 2: run all tests file using early-accept with 1 min time-out
$ python test_solver.py all -appr 1 -time 1


- New constraint files.
New constraints formalized in core constraint language are acceptable if the 
predicates parts can be understood by Z3. 

Example 3: new constraint file using (2.1) in Figure 1:
 L <: ax And az <: ax And ax <: L;
 (d>0) => H <: ay;
 (Not(d>0)) => L <: ay;
 (d>0) => H<: ay;
 (d<0)=> ay<:ax;

User can create a "new.con" file under the tests/ folder with content above and 
run with any settings in the usage.
 

- Code extension
The current code follows modular design. Key functionality of a component is 
implemented in a base class. Extension for parser, lattice, partition algorithm 
and solver can benefit from the base implementation and not be tangled by other 
components. Future user can extend the current version with implementation of 
their own in a straightforward manner. 
Here is a table for components and classes:
-----------------------------------------------------------------
| Components    |    Base class     | Current implementation    |
| lattice       | Lattice           | TwoPointLattice           |
| parser        |CoreConstraintParser| LeftJoinParser           |
| partitioning  |PartitionContext   | SequentialPartition, CombinationPartition|
| solver        |PartitionDerivationSolver| TestSolver          |
-----------------------------------------------------------------

Example 4: new partition algorithm, Optimized Combinational Partitioning. The 
code is available at the end of partt.py(Commented out). 
1. Implement the functionality:
__init__(): specify the initial state of the program
init_partt(): specify the initialization of partition algorithm
next_partt(): how to generate the next partition. self.stop.partt: keep track 
of stop condition

In this example, uncomment the line 148-178 in partt.py. 

2. Specify the new options for the extensions.
Uncomment the Line 24, 29 in globals.py and Line 163,164 in test_solver.py. 

3. Now user can run the new implementation using:

$ python test_solver.py tests/dsram.con -partt 2

"OpCombinationPartition" will show up in the debug message to indicate the new 
implementation is in use.

