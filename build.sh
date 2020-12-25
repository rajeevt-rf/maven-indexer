#!/bin/bash

DDIR="$(pwd)/indexer-examples/indexer-examples-basic"
clspath=${DDIR}/target/classes:${DDIR}/target/dependency/*
srcpath="${DDIR}/src/main/java:${DDIR}/cli/src/main/java"

#java -classpath ${clspath} org.apache.maven.indexer.examples.BasicUsageExample

build() {
    mvn clean package -Drat.numUnapprovedLicenses=100 -Dcheckstyle.skip -DskipTests
    mvn dependency:copy-dependencies 
}

debug() {
    jdb -sourcepath ${srcpath} -classpath ${clspath} ${jdefopts} org.apache.maven.indexer.examples.BasicUsageExample
}

run() {
    java -classpath ${clspath} ${jdefopts} org.apache.maven.indexer.examples.BasicUsageExample
}

clean() {
    mvn clean
}

case "${@}"
in
    ("build") build ;;
    ("clean") clean ;;
    ("run") run ;;
    ("debug") debug ;;
    (*) echo "$0 [ build | run | clean | debug ]" ;;
esac