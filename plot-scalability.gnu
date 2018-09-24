#     This file is part of Derivation Solver. Derivation Solver provides
#     implementation of derivation solvers for dependent type inference.
# 
#     Copyright (C) 2018  Peixuan Li
# 
#     Derivation Solver is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Derivation Solver is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
# 
set key tmargin horiz font ",12"
set term postscript color #font "Times New Roman"
set output "result/scalability.eps"
set yrange [:80000]
set xrange [0.8:250]
set xlabel 'Number of Predicates'
set ylabel 'Execution Time (in seconds)'
set logscale y
set logscale x
set size 0.6,0.6
set format y "10^{%L}"
set ytics (0.00001,0.0001,0.001,0.01,0.1,1,10,100) 

set style line 1 lt 1 lc rgb "red" lw 1
set style line 2 lt 3 lc rgb "blue" lw 1
set style line 3 lt 2 lc rgb "orange" lw 1

set object rectangle from 0.8, 1000 to graph 1, 1 \
	fillcolor rgb 'gray' fillstyle transparent solid 0.3 noborder

# replace time out points
array count[3]
do for [i=1:3] { 
  count[i] = 0 
}

file = ARG1
#file = "result/all-time_3333_13_21_34.csv"
filter(x,y,z) = (x>180 ? (count[y] = count[y] + 1, 500*(4**(z+1-y))) : x)

f(x,y,z)= y>0.5 ? filter(x,z,3) : 0

stats file using 2:(f($6,$3,1)) name 'A' nooutput
stats file using 2:(f($5,$3,2)) name 'B' nooutput
stats file using 2:(f($4,$3,3)) name 'C' nooutput

do for [i=1:3] { 
    set label "".count[i] at 190, 500*(4**(4-i)) font ",12"
}

set label "Time Out" at 1, 8000 

# plot points above threshold
plot file using 2:(f($6,$3,1)) title "OneShot" ls 1, \
     file using 2:(f($5,$3,2)) title "EarlyAccept" ls 3, \
     file using 2:(f($4,$3,3)) title "Hybrid" ls 2, \

!epstopdf result/scalability.eps
#!pdftk temp.pdf cat 1east output performance.pdf
