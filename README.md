# DNS_diver
A collection of scripts figure out which CDN provider works for whichever website. 
## Usage:
```
usage: query_dns.py [-h] [--url URL] [--use_cache USE_CACHE] [--output_file OUTPUT_FILE] [--company COMPANY]

Checks ~300 DNS servers to find the CDN provider for a specified URL endpoint.

optional arguments:
  -h, --help            show this help message and exit
  --url URL             enter a url that needs a CDN to be served
  --use_cache USE_CACHE
                        1 or 0 that determines whether you use cache.csv
  --output_file OUTPUT_FILE
                        string that ends in .csv for the output data.
  --company COMPANY     generally what company the url serves

```
