#!/usr/bin/env python
"""
#######################################################################################
# cpe2ga.py
# Project General
#
#
# Created by mehran on 12 / 30 / 2020.
# Copyright © 2020 Rapidfort Inc. All rights reserved.
#
#######################################################################################
"""

import os
import sys
import re
import time

import mef


def _print_usage(file=sys.stdout):
    print(f"\nUsage: {os.path.basename(sys.argv[0])} <cpe-prod-list-file> <artifact-group-file>", file=file)


def _main():
    if len(sys.argv) == 1:
        _print_usage()
        return 0

    if len(sys.argv) != 3:
        _print_usage(sys.stderr)
        return 1

    prod_list_filename = sys.argv[1]
    artifact_group_filename = sys.argv[2]

    mef.tsprint(f"Reading artifact group file {artifact_group_filename}...")
    ag_words_to_lines_idx_dict = {}

    with open(artifact_group_filename, "r") as ag_file:
        ag_lines = ag_file.readlines()
        for i, line in enumerate(ag_lines):
            line = line.strip()
            ag_words = re.split(r'-|_|\.|,', line)
            for word in ag_words:
                if word in ag_words_to_lines_idx_dict:
                    line_idx_set = ag_words_to_lines_idx_dict[word]
                else:
                    line_idx_set = set()
                    ag_words_to_lines_idx_dict[word] = line_idx_set

                line_idx_set.add(i)

    mef.tsprint(f"Processing product list file {prod_list_filename}...")
    num_no_cands = 0

    #time.sleep(100)
    with open(prod_list_filename, "r") as prod_file:
        prod_lines = prod_file.readlines()
        for i, line in enumerate(prod_lines):
            line = line.strip()
            #if ((i+1) % 50) == 0:
            #    mef.tsprint(f"{i+1}/{len(prod_lines)} processed...")

            prod_words = line.replace("\\", "").split("_")
            #candidates = []
            line_idx_scores_dict = {}
            for word in prod_words:
                line_idx_set = ag_words_to_lines_idx_dict.get(word, set())
                for lidx in line_idx_set:
                    if lidx in line_idx_scores_dict:
                        line_idx_scores_dict[lidx] += 1
                    else:
                        line_idx_scores_dict[lidx] = 1

            # fix scores to 'percent matched'
            for lidx in line_idx_scores_dict:
                line_idx_scores_dict[lidx] = line_idx_scores_dict[lidx] * 100.0 / len(prod_words)

            if len(line_idx_scores_dict) == 0:
                num_no_cands += 1
            else:
                print(line)

            #if len(line_idx_scores_dict) == 0:
            #    num_no_cands += 1
            #    print(f"{i+1}/{len(prod_lines)} - {line} : ({num_no_cands}) No Candidates.")
            #else:
            #    sorted_cands = [(lidx, score) for lidx, score in sorted(line_idx_scores_dict.items(),
            #                                                            key=lambda item: item[1])]
            #    print("--------")
            #    print(f"{line} : {len(line_idx_scores_dict)} candidates:")
            #    for cand in sorted_cands:
            #        print(f"   {cand[1]:4.1f} {ag_lines[cand[0]].strip()}")

        mef.tsprint(f"Done. {num_no_cands} entries with no candidates...")

    return 0


if __name__ == "__main__":
    #print(" ".join(sys.argv))  # debug: print cmd line
    try:
        sys.exit(_main())
    except KeyboardInterrupt:       # don't print python trace backs
        # we don't really need this since we catch SIGINT with the signal handler, but for reference...
        print("\nInterrupted.\n")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)             # pylint: disable=protected-access
