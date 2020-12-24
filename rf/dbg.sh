#!/bin/bash

#-classpath "classes:dependency/aopalliance-1.0.jar:dependency/cdi-api-1.0.jar:dependency/commons-io-2.5.jar:dependency/commons-lang3-3.5.jar:dependency/guava-20.0.jar:dependency/guice-4.1.0.jar:dependency/hamcrest-core-1.3.jar:dependency/indexer-core-6.1.0-SNAPSHOT.jar:dependency/javax.annotation-api-1.2.jar:dependency/javax.inject-1.jar:dependency/jsoup-1.7.2.jar:dependency/jsr305-3.0.2.jar:dependency/junit-4.13.jar:dependency/lucene-analyzers-common-5.5.5.jar:dependency/lucene-backward-codecs-5.5.5.jar:dependency/lucene-core-5.5.5.jar:dependency/lucene-highlighter-5.5.5.jar:dependency/lucene-join-5.5.5.jar:dependency/lucene-memory-5.5.5.jar:dependency/lucene-queries-5.5.5.jar:dependency/lucene-queryparser-5.5.5.jar:dependency/lucene-sandbox-5.5.5.jar:dependency/maven-model-3.5.2.jar:dependency/maven-resolver-api-1.1.0.jar:dependency/maven-resolver-util-1.1.0.jar:dependency/org.eclipse.sisu.inject-0.3.3.jar:dependency/org.eclipse.sisu.plexus-0.3.3.jar:dependency/plexus-classworlds-2.5.2.jar:dependency/plexus-component-annotations-2.0.0.jar:dependency/plexus-utils-3.0.24.jar:dependency/slf4j-api-1.7.25.jar:dependency/slf4j-simple-1.7.5.jar:dependency/wagon-http-lightweight-2.12.jar:dependency/wagon-http-shared-2.12.jar:dependency/wagon-provider-api-2.12.jar"

DDIR="/home/ubuntu/rapidfort/experiment/maven-indexer/indexer-examples/indexer-examples-basic"
clspath=${DDIR}/target/classes:${DDIR}/target/dependency/*
#srcpath="${DDIR}/src/main/java:${DDIR}/cli/src/main/java"
srcpath="${DDIR}/src/main/java"

#java -classpath ${clspath} org.apache.maven.indexer.examples.BasicUsageExample
jdb -sourcepath ${srcpath} -classpath ${clspath} ${jdefopts} org.apache.maven.indexer.examples.BasicUsageExample

