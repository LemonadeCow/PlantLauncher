#!bin/bash

file=$1
executable=$(grep -m1 "^Exec=" "$file")
echo ${executable:5}
 