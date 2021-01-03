#!/bin/bash

CVE_FOLDER=${1:-/home/ubuntu/.cache/vuln-list-update/vuln-list/ghsa/maven}
NVD_FOLDER=${2:-/home/ubuntu/.cache/vuln-list-update/vuln-list/nvd}

flatten_json() {
    jq -r ' paths(scalars) as $p | [ ( [ $p[] | tostring ] | join(".") ), ( getpath($p) | tojson )] | join(" = ") ' $1
}

find_cpes_for_cve() {
    json_file="${1}.json"
    jsons=$(find "${NVD_FOLDER}" | grep "${json_file}")
    for i in "${jsons[@]}"
    do
        flatten_json "${i}" | grep 'cpe23Uri' | awk '{print $3}'
    done
}

find_all_cves() {
    mapfile -d $'\0' jsons < <(find "${CVE_FOLDER}" -type f -print0)
    for j in "${jsons[@]}"
    do
        cve=$(flatten_json "${j}" | grep 'CVE-' | grep 'Advisory.Identifiers' | awk '{print $3}')
        cve=$(echo "$cve" | tr -d '"')
        if [ -z "${cve}" ]; then
            echo "!!!!!NON CVE vulns"
        else
            echo "$cve: ${j}"
            find_cpes_for_cve $cve
        fi
    done
}

find_all_cves
