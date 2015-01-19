#!/bin/sh
export DYLD_LIBRARY_PATH=/Users/sam/git/NSASurveillanceBot/src/export/darwin/lib:$LD_LIBRARY_PATH
java -cp /Users/sam/git/NSASurveillanceBot/src/java/jnaerator-0.11-SNAPSHOT-20121008.jar:/Users/sam/git/NSASurveillanceBot/src/java/bin pbots_calc.Calculator $@