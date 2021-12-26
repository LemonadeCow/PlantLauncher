#!bin/bash

file=$1
icon=$(grep -m1 "^Icon=" "$file")
echo ${icon:5}