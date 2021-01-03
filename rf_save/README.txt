- get a list of unique artifact/group ids:

cut -f 1,2 -d',' artifactinfo.txt | sort -u > ag-all.uniq.txt

- get a list of unique CPE products:

cut -f 2 vendor-product-list.txt | sort -u | product-unique.list

- run cpe2ga.py on product-unique list and comment the code to produce only products that have matches
to artifact-groups file. (TODO: MEF: make this an argument to cpe2ga)

./cpe2ga2.py product-unique.list ag-all.uniq.txt | tee prod-uniq-matched-pass1.list

- look up from this list in vendor-products index file to get a list with vendors included:

while read line ; do grep -F $'\t'"$line" vendor-product-list.txt ; done < prod-uniq-matched-pass1.list | sort -u | sort -k2 -t $'\t' > vend-prod-uniq-matched-pass1.list

- extract the vendors and look them up in the artifacts list:

cut -f1 vend-prod-uniq-matched-pass1.list | sort -u > y.vends

while read line ; do grep -F "$line" ag-all.uniq.txt > /dev/null ; [ "$?" == "0" ]  && echo $line ; done < y.vends | tee y.vends.matched

- now extract only vendors that matched

while read line ; do grep "^$line"$'\t' vend-prod-uniq-matched-pass1.list ; done < y.vends.matched | tee vend-prod-uniq-matched-pass2.list

- get a quick list of vendor/prods for which we don't find a match in the artifact/group list:

for vend in $(cut -f 1 vend-prod-uniq-matched-pass2.list | sort -u) ; do ./check-vend.sh vend-prod-uniq-matched-pass2.2.list "$vend" | grep UNMATCHED ; done | tee unmatched.list

- next inspect this unmatched file manually, and remove all lines that should be left for consideration despite no match found

- edit the file and remove stuff that doesn't look like they belong!
    - delete activex stuff (active_x also)
    - delete firmware
    - delete asus, atari, d-link, dlink, divx, angularjs, android, skype, aol, .net stuff, lots of apple stuff, lots of
      autodesk stuff, avast, avg, avira, bitcoin stuff, blackberry, brave, broadcom, all driver stuff, all wireless stuff,
      all novell, norton, nvidia, all sun, mcafee, nokia, sony, businessobjects, canon, checkpoint, windows stuff, mircorsoft apps,
    - delete 3m, 68k, a-ftp, a-pdf, abacus, abbyy, abine, absolute, acid,
    - use checkvend.sh to delete vendor/prod lines with no match
        e.g.  ./check-vend.sh vend-prod-uniq-matched-pass2.2.list cisco
        then replace all "cisco" entries with the output.
        NOTE: This will have false negatives when cpe vendor does not match with the group id in any way. e.g. redhat/underfow
      


