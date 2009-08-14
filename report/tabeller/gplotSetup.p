set term png 
set out 'ngram.png'
set xlabel "Number of articles to process"
set ylabel "Time (in seconds)"
set xr [100:1200]
plot "ngramGNUPlot.dat" using 1:2 title "ngrams" with linespoints

set out 'work.png'
set xlabel "Number of articles in corpora"
set ylabel "Time (in seconds)"
set xr [100:1200]
plot "ultimateGNUPlot.dat" using 1:2 title "n-grams" with linespoints

replot
