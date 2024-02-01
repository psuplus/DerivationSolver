# Derivation Solver 

This package provides implementation of derivation solvers for dependent type 
inference. It consists of four constraint solvers, i.e., one-shot, 
early-accept, early-reject and hybrid solver along with two partition 
algorithms: sequential and combinational partitioning. A parser for the core 
constraint language and plotting scripts are also available in the package. 

## Dependency

The solvers are implemented in Python with external support from Z3.  Our 
evaluation is set up using Python 3.7.10 and Z3 4.5.0, but the implementation 
is not specialized to these versions. It is expected to be compatible for most 
of the existing version of Python and Z3. After evaluation data are 
obtained, we use gnuplot to visualize the result. 
In summary, here is the list of dependency:

- [python](https://www.python.org/) >=3.7
- [Z3](https://github.com/Z3Prover/z3) >=4.5
- [gnuplot](http://www.gnuplot.info/)


** Note that Z3 needs to be installed and be binded to the python in use. 
Here is a quick test to verify the Z3 installation by using our Z3 unit test cases:
```
python3 z3supp.py
```
If all test cases pass, it means that Z3 works as expected.


## Quick Taste

Here is a quick demo to run a small test case(dsram.con). By default, the 
 test will solve the constraints in `tests/dsram.con` using all three 
different solvers across two partition algorithms(6 unit tests in total):
```
$  ./solver.py -f dsram.con
```

Debug message will be printing out during the execution and the execution time 
is saved under the result folder with name in form of 
'[test file name]+[timestamps].csv'. 
Thus, you should find a result file "dsramXXXXXXXX.csv" in result folder when 
the it is complete. The file contains the execution time for all 6 test cases. 



## Reproducing the evaluation result
To reproduce the evaluation result reported in the paper, here are the steps:
1. run all the test files with three solvers(no early-reject since most of the 
test cases are solvable and early-reject solver is not useful for solvable 
cases) across two partition algorithms:
   ```
   $  ./solver.py -f all
   ```
    This could take hours(~8h in our case) to finish. A brief break-down:
100 test file * 3 approaches * 2 partition algorithms = 600 unit test cases.

    When it is done, a performance file "all[timestamp].csv" should be produced 
under result/ folder. We include our previous result file 
"all-time_3333_13_21_34.csv" in the folder. We use this 
file as example for the next steps.

2. plot the performance graph[Fig 9] using the result file. The file 
performance graph, named "performance-file.pdf" should be produced 
under result\ folder.
    ```
    $ gnuplot -c plot-filewise.gnu result/all-time_3333_13_21_34.csv
    ```

3. plot the scalability graph[Fig 10] using the result file. The scalability 
graph, named "scalability.pdf" should be produced under result\ folder.
    ```
    $ gnuplot -c plot-scalability.gnu result/all-time_3333_13_21_34.csv
    ```
4. plot the sequential vs combination graph[Fig 11] using the result file. The 
comparison graph, named "seq-comb.pdf" should be produced under result\ folder.
    ```
    $ gnuplot -c plot-seq-comb.gnu result/all-time_3333_13_21_34.csv
    ```

## Reuse 

The current implementation provides multiple levels of reuse for future needs.

### Tuning running parameters.
The complete usage of the code is as follow:
```
usage: solver.py [-h] [-f FILE] [-partt PARTITION [PARTITION ...]] [-appr APPROACH [APPROACH ...]] [-t TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The test file is either a single file *.con assuming under tests/ folder, or `all` all the files under the tests. folder. Default=all.
  -partt PARTITION [PARTITION ...], --partition PARTITION [PARTITION ...]
                        Partition algorithm: (seq, comb). Default=all.'seq' for sequential, 'comb' for combinational.
  -appr APPROACH [APPROACH ...], --approach APPROACH [APPROACH ...]
                        Approach: (hybrid, early-accept, one-shot, early-reject). Default=[hybrid, early-accept, one-shot]
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in minutes. Default=3
```

Example 1: run tests/dsram.con using hybrid solver with sequential partitioning:
```
$ ./solver.py -f dsram.con -partt seq -appr hybrid
```

Example 2: run all tests file using early-accept with 1 min time-out
```
$ ./solver.py -f all -appr early-accept -t 1
```

### New constraint files.
New constraints formalized in core constraint language are acceptable if the 
predicates parts can be understood by Z3. 

Example 3: new constraint file using (2.1) in Figure 1:
```
L <: ax And az <: ax And ax <: L;
(d>0) => H <: ay;
(Not(d>0)) => L <: ay;
(d>0) => H<: ay;
(d<0)=> ay<:ax;
```

User can create a `new.con` file under the tests/ folder with content above and 
run with any settings in the usage.
 

### Code extension

The current code follows modular design. Key functionality of a component is 
implemented in a base class. Extension for parser, lattice, partition algorithm 
and solver can benefit from the base implementation and not be tangled by other 
components. Future user can extend the current version with implementation of 
their own in a straightforward manner. 
Here is a table for components and classes:

|  Components    | Base class | Current implementation |
|:--------------:|:----------:|:----------------------:|
| lattice       | Lattice           | TwoPointLattice           |
| parser        |CoreConstraintParser| LeftJoinParser           |
| partitioning |PartitionContext | SequentialPartition, CombinationPartition|
| solver        |PartitionDerivationSolver| TestSolver          |
-----------------------------------------------------------------

Example 4: new partition algorithm, Optimized Combinational Partitioning. The 
code is available at the end of [partt.py](./partt.py)(Commented out). 
1. Implement the functionality:
    - `__init__()`: specify the initial state of the program
    - `init_partt()`: specify the initialization of partition algorithm
    - `next_partt()`: how to generate the next partition. 
    - `self.stop.partt`: keep track 
of stop condition
    
    In this example, uncomment the line 130-160 in [partt.py](./partt.py). 

1. Specify the new options for the extensions.
Uncomment the Line 6, 11 in [globals.py](./globals.py) and Line 81,82 in [solver.py](./solver.py). 

3. Now user can run the new implementation using:
    ```
    $ ./solver.py -f dsram.con -partt opcomb
    ```
    "OpCombinationPartition" will show up in the debug message to indicate the new implementation is in use.

