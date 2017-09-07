#!/bin/bash
PATH="$(pwd)/tests/bin/:$PATH" nosetests -v -s --with-coverage --cover-xml-file=$(pwd)/coverage.xml --cover-xml 
