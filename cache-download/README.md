Download Caching
===

`cache-download.py` is a script which "warms up" a root server's download cache.

It looks for `prefetch` statements in fixlets which belong to the root server's external sites and downloads these files to the cache as their SHA-1 hash. This script accepts a variety of parameters in addition to the ones specified for [example.py](../example/README.md). 

Parameters
---

These options specify configurable filters to the set of files downloaded:
 * `-x, --sites` Specify a list of sites to prefetch from
 * `-m, --maxsize` Avoids caching files with sizes larger than some size in bytes (defaults to 1 gigabyte)
 * `-t, --type` Specify a filetype extension to prefetch for
 * `-r, --url` Specify a base URL to prefetch from
 * `-n, --names` Specify a list of filenames to prefetch

In addition, `cache-download.py` accepts a few miscellaneous options:
 * `-v, --verbose` Print more output as the script is running
 * `-d, --dry` Only print names of files to cache (do not actually run downloads)

Example
---
This command will cache all downloads of files with a `.exe` extension with a size less than 0.1 GB:

    python cache-download.py --user bigfix --password bigfix --server localhost:52311 --type exe --maxsize 100000000
