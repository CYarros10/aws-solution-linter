#!/bin/bash

echo "--------------------------------"
echo "Linting Solution..."
echo "--------------------------------"


echo "--------------------------------"
echo "linting python..."
echo "--------------------------------"

if [[ -d scripts ]]
then
    for file in scripts/*.py
    do
        pylint $file 
    done
else
    echo "ERROR: please create a scripts/ directory for python/javascript"
fi

echo "--------------------------------"
echo "linting cloudformation..."
echo "--------------------------------"

if [[ -d templates ]]
then
    for file in templates/*.yaml
    do
        yamllint $file
        cfn-lint validate $file
        cfn_nag_scan --input-path $file
    done
else
    echo "ERROR: please create a templates/ directory for cloudformation templates."
fi


echo "--------------------------------"
echo "linting markdown..."
echo "--------------------------------"

if [[ -f readme.md ]]
then
	mdl readme.md
else
	echo "please create a readme.md file"
fi
