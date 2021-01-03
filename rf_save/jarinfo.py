#!/usr/bin/env python3

"""
#######################################################################################
#
# jarinfo.py
# Project package analyzer
#
# Extract info from jar files
#
# Created by mehran on 01 / 02 / 2021.
# Copyright © 2021 Rapidfort Inc. All rights reserved.
#
#######################################################################################
"""

import sys
import os

from zipfile import ZipFile
from javatools.manifest import Manifest
#from xml.etree import ElementTree               # MEF: vulnerable
from defusedxml import ElementTree

import mef


# for reference by other modules
JAR_PATTERNS = (
    "*.ear",
    "*.jar",
    "*.rar",
    "*.sar",
    "*.war",
)


class POM():
    """ Read and parse a POM file """

    _namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}

    def __init__(self, file_source):
        """ file_source can be a filename or a file object """
        self._file_source = file_source
        self._tree = ElementTree.parse(self._file_source)
        root = tree.getroot()
        self._group_id = root.findall(".//xmlns:groupId", namespaces=self._namespaces)
        self._artifact_id = root.findall(".//xmlns:artifactId", namespaces=self._namespaces)

    def get_dependencies(self):
        root = tree.getroot()
        deps = root.findall(".//xmlns:dependency", namespaces=self._namespaces)
        ret = []
        for d in deps:
            artifact_id = d.find("xmlns:artifactId", namespaces=self._namespaces)
            version = d.find("xmlns:version", namespaces=self._namespaces)
            ret.append((artifact_id, version))

        return ret

    def get_group_id(self):
        return self._group_id

    def get_artifact_id(self):
        return self._artifact_id


class JarInfo():
    """ Utilitiy class to extract info form a jar file... """

    _manifest_filename = "META-INF/MANIFEST.MF"

    def __init__(self, filename: str):
        self._filename = filename
        self._zip = ZipFile(filename)

    def get_manifest(self):
        """ Return a Manifest object loeaded from the jar file """
        try:
            data = self._zip.read(self._manifest_filename)
        except KeyError:
            raise RuntimeError(f"{self._manifest_filename} not found in {self._filename}.")

        mf = Manifest()
        mf.parse(data)
        return mf

    def get_entry_infos(self):
        """ Return a list fo ZipInfo objects for all entries in the jar file """
        return self._zip.infolist()

    def get_pom_names(self):
        """ Return a list of POM file entries in the jar file """
        poms = []
        for zinfo in self.get_entry_infos():
            if not zinfo.is_dir() and zinfo.filename.upper().startswith("META-INF") and os.path.basename(zinfo.filename).lower() == "pom.xml":
                poms.append(zinfo.filename)
        return poms


def _main():
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <jarfilename>", file=sys.stderr)
        return 1

    import pdb ; pdb.set_trace()

    jfile = sys.argv[1]
    ji = JarInfo(jfile)
    mf = ji.get_manifest()

    print("Manifest main section:")
    for k, v in sorted(mf.items()):
        print("  %s: %s" % (k, v))

    for _name, sect in sorted(mf.sub_sections.items()):
        print()
        print("Manifest sub-section:")
        for k, v in sorted(sect.items()):
            print("  %s: %s" % (k, v))

    print(ji.get_pom_names())
    return 0


if __name__ == "__main__":
    #mef.run_main(_main, print_exception_trace=True)
    mef.run_main(_main)     # run_main() handles cleaning up stack trace prints, keyboard interrupt, broken pipe, etc.

