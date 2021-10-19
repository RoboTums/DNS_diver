#!/bin/bash
FILENAME="result_"
FILENAME+="$1_"
FILENAME+="$2.txt"
dig @$1 $2 >> "./tmp/${FILENAME}"
