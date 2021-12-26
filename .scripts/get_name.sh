#!bin/bash

file=$1
name=$(grep -m1 "^Name=" "$file")
echo ${name:5}
