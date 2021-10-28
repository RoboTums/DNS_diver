#!/usr/bin/env python3

"""
usage: query_dns.py [-h] [--url URL] [--output_file OUTPUT_FILE]

Checks ~300 DNS servers to find the CDN provider for a specified URL endpoint.

optional arguments:
  -h, --help            show this help message and exit
  --url URL             enter a url that needs a CDN to be served
  --output_file OUTPUT_FILE
                        string that ends in .csv for the output data.
"""
import requests 
import pandas as pd
from datetime import date
from collections import defaultdict
import argparse
import multiprocessing
import os
import functools
import time
import subprocess
import shlex

def parse_IP(ip_str):
    #first check if IPv4 or IPv6:
   if ':' in ip_str:
        #ipv6
        split_list = ip_str.split(':')[0:6]
        acc = ""
        for char in split_list[-1]:
            if char.isdigit():
                acc += char
            else:
                break
        split_list[-1] = acc
        return ":".join(split_list)
   else:
        split_list = ip_str.split('.')[0:4]
        acc = ""
        for char in split_list[-1]:
            if char.isdigit():
                acc += char
            else:
                break
        split_list[-1] = acc
        return ".".join(split_list)

def read_ASN_database():
    return pd.read_csv(
            'ip_asn_db.tsv',
            names="range_start range_end AS_number country_code AS_description".split(' '),
            delimiter='\t'
        )

def get_public_dns_servers(dns_server_website="https://dnschecker.org/public-dns/us"):
    resp = requests.get(dns_server_website)
    dns_server_table = pd.read_html(resp.text)[0]
    #clean DNS_Server_table. Just some regex lamdba on an IP address, amazon interview question
    dns_server_table['IP Address'] = dns_server_table['IP Address'].apply(lambda x: parse_IP(x))
    return dns_server_table

def convert_ipv4(ip):
    return tuple(int(n) for n in ip.split('.'))
def check_ipv4_in(addr, start, end):
    return convert_ipv4(start) < convert_ipv4(addr) < convert_ipv4(end)

def read_cache():
    return pd.read_csv('cache.csv',index_col=0)

def query_dns(ip_address,url,dns_server_table,today):
    cmd = f"./bash_query.sh {ip_address} {args.url}"
        #print(cmd)
    proc=subprocess.Popen(shlex.split(cmd))

    current_series = dns_server_table[dns_server_table["IP Address"] == ip_address]

    return {
                'ip_address':ip_address,
                'location':current_series['Location'].iloc[0].split('\n')[0],
                'reliability':current_series['Reliability'].iloc[0].split('\n')[0],
                'ASN':None,
                'date': today,
                'url':url

                }
        
if __name__ == '__main__':
    tic = time.perf_counter()
    os.makedirs('tmp',exist_ok=True)
    parser = argparse.ArgumentParser(description='Checks ~300 DNS servers to find the CDN provider for a specified URL endpoint.')
    parser.add_argument('--url', type=str, default="images-na.ssl-images-amazon.com", help="enter a url that needs a CDN to be served")
    parser.add_argument('--use_cache', type=int, default=1, help="1 or 0 that determines whether you use cache.csv")
    parser.add_argument('--output_file', type=str, default="us_aws_cdn.csv", help="string that ends in .csv for the output data.")
    parser.add_argument("--company",type=str, default="AMZN", help="generally what company the url serves")
    parser.add_argument("--cores",type=int, default=6,help="number of CPU cores to use. Default is 6. -1 is all CPU cores. ")
    args = parser.parse_args()
    #parse cores. 
    if parser.cores == -1:
        num_cores = multiprocessing.get_num_cores()
    else:
        num_cores = parser.cores
    #recover cached DNS
    if args.use_cache == 1:
        dns_server_table = read_cache()
    else:
        dns_server_table = get_public_dns_servers()
    #multiprocessing alloc
    proc_pool = multiprocessing.Pool(None)

    today = date.today().strftime("%m/%d/%Y")
    ip_data = []
    f = functools.partial(query_dns, url=args.url, dns_server_table=dns_server_table,
            today = date.today().strftime("%m/%d/%Y") 
            )

    #we curry the dns server table 
    results = proc_pool.map(
                    f,
                    dns_server_table['IP Address']
            )
    
            
    ip_table = pd.DataFrame(results)
    
    #parse /tmp/ dig outputs parallelized-like, i.e
    
    asn_table = read_ASN_database()


    #asn_data.to_csv('debug.csv')

    #asn_data.to_csv(date.today().strftime("%m_%d_%Y")+"_"+args.output_file.split('.')[0] + '_verbose_test.csv')
    toc = time.perf_counter()
    print(f"Found CDN providers for {args.url} in {toc - tic:0.4f} seconds")

    
#    raw_output = output.split('ANSWER SECTION')
#    if len(raw_output) > 1:
#        #answer is received.
#        ASN = raw_output[-1].split('IN\tA')[-1].split('\n')[0].split('\t')[-1]
#    else:
#        ASN = None