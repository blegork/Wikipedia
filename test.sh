#!/bin/bash

TIME=15

array=("Category:Agriculture" "Category:Subfields_of_computer_science" "Category:Emerging_technologies" "Category:Agricultural_technology" "Category:Rural_society" "Category:Forestry" "Category:Forest_modelling")


#durata test tutte le categorie ~ 1890 minuti(1d 7h 30 minuti)
for j in "${array[@]}" ; do
	#durata test ~ 135 minuti( 2h 15 minuti )
	for (( i = 1 ; i <= TIME ; i += 1 )) ; do
		echo "Inizio test"
		echo "python3 main.py -d 15 -c $j -w 100 -t $i -p"
		python3 main.py -d 15 -c $j -w 100 -t $i
		
	done
	#durata test ~ 135 minuti( 2h 15 minuti )
	for (( i = 1 ; i <= TIME ; i += 1 )) ; do
		echo "Inizio test"
		echo "python3 main.py -d 15 -c $j -w 100 -t $i -p"
		python3 main.py -d 15 -c $j -w 100 -t $i -p
		sleep 1m
	done
done
