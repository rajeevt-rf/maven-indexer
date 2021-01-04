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
from rf_log import LOG


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

    _expected_namespace = "http://maven.apache.org/POM/4.0.0"

    def __init__(self, filesource):
        """ file_source can be a filename or a file object """
        self._filename = filesource if isinstance(filesource, str) else filesource.name
        self._tree = ElementTree.parse(filesource)
        self._root = self._tree.getroot()

        root_tag = self._root.tag.lower()
        if root_tag == "project":
            # no namespace in POM file
            LOG.warning(f"POM file {self._filename} has no namespace.")
            self._namespaces = {'': ''}
        elif root_tag.startswith("{") and root_tag.endswith("}project"):
            ns_str = self._root.tag[1:-8]
            self._namespaces = {'': ns_str}
            if ns_str != self._expected_namespace:
                LOG.warning(f"POM file {self._filename} has namespace {ns_str} instead of {self._expected_namespace}.")
        else:
            raise RuntimeError(f"Invalid POM file {self._filename}. No project root.")

        self._model_version = self._elem_text("modelVersion")

        self._group_id = self._elem_text("groupId")
        self._artifact_id = self._elem_text("artifactId")
        self._version = self._elem_text("version")
        self._name = self._elem_text("name")
        self._desc = self._elem_text("description")
        self._url = self._elem_text("url")

        parent_elem = self._elem("parent")
        if parent_elem is not None:
            self._parent_group_id = self._elem_text("groupId", root=parent_elem)
            self._parent_artifact_id = self._elem_text("artifactId", root=parent_elem)
            self._parent_version = self._elem_text("version", root=parent_elem)
        else:
            self._parent_group_id = self._parent_artifact_id = self._parent_version = ""

        # inherit the following from parent if missing...
        self._group_id = self._group_id if self._group_id else self._parent_group_id
        self._artifact_id = self._artifact_id if self._artifact_id else self._parent_artifact_id
        self._version = self._version if self._version else self._parent_version

        # organization info
        org_elem = self._elem("organization")
        if org_elem is not None:
            self._org_name = self._elem_text("name", org_elem)
            self._org_url = self._elem_text("url", org_elem)
        else:
            self._org_name = self._org_url = ""

    def _elem(self, tag: str, root=None, findall=False):
        root = self._root if root is None else root
        finder = root.findall if findall else root.find
        return finder(f"./{tag}", namespaces=self._namespaces)

    def _elems(self, tag: str, root=None):
        return self._elem(tag, root=root, findall=True)

    def _elem_text(self, tag: str, root=None):
        elem = self._elem(tag, root=root)
        return elem.text if elem is not None else ""

    def get_filename(self):
        """ Return filename associated with this POM """
        return self._filename

    def get_model_version(self):
        """ Return the POM model version """
        return self._model_version

    def get_group_id(self):
        """ return the groupId """
        return self._group_id

    def get_artifact_id(self):
        """ return the artifactId """
        return self._artifact_id

    def get_version(self):
        """ return the version """
        return self._version

    def get_name(self):
        """ return the name """
        return self._name

    def get_desc(self):
        """ return the description """
        return self._desc

    def get_url(self):
        """ return the project url """
        return self._url

    def get_parent_group_id(self):
        """ return the parent group id """
        return self._parent_group_id

    def get_parent_artifact_id(self):
        """ return the parent artifact id """
        return self._parent_artifact_id

    def get_parent_version(self):
        """ return the parent version """
        return self._parent_version

    def get_org_name(self):
        """ return the organization name """
        return self._org_name

    def get_org_url(self):
        """ return the organization url """
        return self._org_url

    def get_dependencies(self):
        """ get a list of dependencies in the pom file, each a tuple of (artifaceId, version) """
        ret = []
        deps_elem = self._elem("dependencies")
        if deps_elem is not None:
            #deps = deps_elem.findall(".//xmlns:dependency", namespaces=self._namespaces)
            deps = self._elems("dependency", root=deps_elem)
            for dep in deps:
                artifact_id = self._elem_text("artifactId", root=dep)
                version = self._elem_text("version", root=dep)
                ret.append((artifact_id, version))

        return ret


class JarInfo():
    """ Utilitiy class to extract info form a jar file... """

    _manifest_filename = "META-INF/MANIFEST.MF"

    def __init__(self, filename: str):
        self._filename = filename
        self._zip = ZipFile(filename)
        self._infos = self._zip.infolist()

    def get_manifest(self):
        """ Return a Manifest object loeaded from the jar file """
        try:
            data = self._zip.read(self._manifest_filename)
        except KeyError as e:
            raise RuntimeError(f"{self._manifest_filename} not found in {self._filename}.") from e

        manf = Manifest()
        manf.parse(data)
        return manf

    def get_entry_infos(self):
        """ Return a list fo ZipInfo objects for all entries in the jar file """
        return self._infos

    def get_pom_names(self):
        """ Return a list of POM file entries in the jar file """
        poms = [zinfo.filename for zinfo in self._infos
                    if not zinfo.is_dir() and zinfo.filename.upper().startswith("META-INF") and
                        os.path.basename(zinfo.filename).lower() == "pom.xml"]
        return poms

    def get_pom(self, pom_name:str):
        """ Return a POM object for the given POM name """
        with self._zip.open(pom_name) as entry_file:
            return POM(entry_file)

    def get_poms(self):
        pom_names = self.get_pom_names()
        poms = []
        for pname in pom_names:
            poms.append(self.get_pom(pname))
        return poms


def _main():
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <jarfilename>", file=sys.stderr)
        return 1

    #import pdb ; pdb.set_trace()
    jfile = sys.argv[1]
    jinfo = JarInfo(jfile)
    manf = jinfo.get_manifest()

    print("Manifest main section:")
    for k, v in sorted(manf.items()):
        print("  %s: %s" % (k, v))

    for _name, sect in sorted(manf.sub_sections.items()):
        print()
        print("Manifest sub-section:")
        for k, v in sorted(sect.items()):
            print("  %s: %s" % (k, v))

    poms = jinfo.get_poms()
    print(f"{len(jinfo.get_entry_infos())} and {len(poms)} POM entries in jar file...")
    for pom in poms:
        print(f"POM file: {pom.get_filename()}:")
        print(f"    parent groupId      : {pom.get_group_id()}")
        print(f"    parent artifactId   : {pom.get_artifact_id()}")
        print(f"    parent version      : {pom.get_version()}")
        print(f"    groupId             : {pom.get_group_id()}")
        print(f"    artifactId          : {pom.get_artifact_id()}")
        print(f"    version             : {pom.get_version()}")
        print(f"    name                : {pom.get_name()}")
        print(f"    description         : {pom.get_desc()}")
        print(f"    project url         : {pom.get_url()}")
        print(f"    organization name   : {pom.get_org_name()}")
        print(f"    organization url    : {pom.get_url()}")
        #print(pom.get_dependencies())

    return 0


if __name__ == "__main__":
    #mef.run_main(_main, print_exception_trace=True)
    mef.run_main(_main)     # run_main() handles cleaning up stack trace prints, keyboard interrupt, broken pipe, etc.
