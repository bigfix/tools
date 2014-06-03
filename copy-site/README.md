Copy sites
===

`copy-site.py` is a script which copys all of the fixlets from a given 
(enterprise) source site to a given destination site.

To reduce the number of requests made to the destination site,
`copy-site.py` stores a local file, `fixlet_hashes.txt`, which is a 
tab delimited record of the hashes of and ids of fixlets found on the
destination site. `copy-site.py` uses these hashes to determine whether
or not a fixlet on the source site needs to be copied. By default,
this cache file is used for 3 hours starting from when it was created.

Parameters
---

These options are required for operation:
 * `-r, --source-site` Name of the site (not URL) to copy resources from
 * `-d, --destination-site` Name of the site (not URL) to copy resources to
`copy-site.py` also takes optional arguments:
 * `-t, --test` Performs a dry run of the copy operation, to check to 
 see if the copy operation was complete

Example
---
This command will move all fixlets from a site named "BES Support" to a
custom site named "copysite_test".

	python copy-site.py --user bigfix --password bigfix -s https://localhost:52311/ -r "BES Support" -d copysite_test

