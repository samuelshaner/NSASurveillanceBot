#!/bin/sh
export DYLD_LIBRARY_PATH=/Users/sam/git/pbots_calc/export/darwin/lib:$LD_LIBRARY_PATH
python /Users/sam/git/pbots_calc/python/calculator.py $@