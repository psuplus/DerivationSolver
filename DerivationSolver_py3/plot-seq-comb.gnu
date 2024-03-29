set key tmargin horiz font ",12"
set term postscript color #font "Times New Roman"
set output "result/seq-comb.eps"
set yrange [:80000]
set xrange [0:100]
set xlabel 'Constraint File ID'
set ylabel 'Execution Time (in seconds)'
set logscale y
set size 0.6,0.6
set format y "10^{%L}"
set ytics (0.00001,0.0001,0.001,0.01,0.1,1,10,100) 

set style line 1 lt 1 lc rgb "red" lw 1
set style line 2 lt 3 lc rgb "blue" lw 1
set style line 3 lt 2 lc rgb "orange" lw 1

set object rectangle from 0, 1000 to graph 1, 1 \
	fillcolor rgb 'gray' fillstyle transparent solid 0.3 noborder

# replace time out points
array count[3]
do for [i=1:3] { 
  count[i] = 0 
}

file = ARG1
#file = "result/all-time_3333_13_21_34.csv"
filter(x,y,z) = (x>180 ? (count[y] = count[y] + 1, 500*(4**(z+1-y))) : x)

# plot sequential vs combinational 
g(x,y,z)= z<1.5 ? (y<0.5? filter(x,z,2):0) : (y>0.5?filter(x,z,2):0)

stats file using 2:(g($4,$3,1)) name 'A' nooutput
stats file using 2:(g($4,$3,2)) name 'B' nooutput

do for [i=1:2] { 
    set label "".count[i] at 90, 500*(4**(3-i)) font ",12"
}

set label "Time Out" at 1, 32000 
plot file every 2::1 using :(g($4,$3,1)) title "Sequential" ls 1, \
     file every 2::2 using :(g($4,$3,2)) title "Combinational" ls 2, \

!epstopdf result/seq-comb.eps
#!pdftk temp.pdf cat 1east output performance.pdf
