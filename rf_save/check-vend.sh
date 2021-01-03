#!/bin/bash

# given a vendor-products file and a vendor name, look up the group/artifacts file for matches to all
# words for the products for the vendor, and printout only lines from vendor-product file where we find a match

ag_file="ag-all.uniq.txt"
vend_prod_file="${1}"
vend="${2}"

saved_IFS=$IFS
IFS=$'\n'
vend_lines=($(grep "^${vend}"$'\t' "${vend_prod_file}"))
IFS=$saved_IFS
err=$?
if [ $err != 0 ] ; then
    exit $err
fi

vend_search=${vend//-/\\-}
#echo $vend_prod_file $vend $vend_search

matched=0
for vline in "${vend_lines[@]}" ; do
    prod=${vline/*	/}                  # extract product
    prod_search=${prod//_/\\|}          # build search pattern for any of the words in product (_ is space in cpe)
    #prod_search=${prod//-/\\|}
    prod_search=${prod_search//-/\\-}
    prod_search=${prod_search//./\\.}
    #echo $vline "--" $prod "--" $prod_search

    grep -iw "${vend_search}" "${ag_file}" | grep -i "${prod_search}" > /dev/null

    if [ ${PIPESTATUS[0]} == 0 -a ${PIPESTATUS[1]} == 0 ] ; then
        echo $vline
        ((matched++))
    else
        echo "UNMATCHED: $vline"
    fi
done

echo "${#vend_lines[@]} vendor lines --> $matched matched lines."

