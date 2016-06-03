#!/bin/bash
for dir in `ls -d */`
do 
    nohup python $dir/*serv.py &
done
