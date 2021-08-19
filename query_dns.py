#!/usr/bin/python3
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
import subprocess
import pandas as pd
from datetime import date
import shlex
import re
from collections import defaultdict
from tqdm import tqdm
import argparse


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
    
def get_public_dns_servers(dns_server_website="https://dnschecker.org/public-dns/us"):
    resp = requests.get(dns_server_website)
    dns_server_table = pd.read_html(resp.text)[0]
    #clean DNS_Server_table. Just some regex lamdba on an IP address, amazon interview question
    dns_server_table['IP Address'] = dns_server_table['IP Address'].apply(lambda x: parse_IP(x))
    return dns_server_table
def read_cache():
    return pd.read_csv('cache.csv',index_col=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checks ~300 DNS servers to find the CDN provider for a specified URL endpoint.')
    parser.add_argument('--url', type=str, default="images-na.ssl-images-amazon.com", help="enter a url that needs a CDN to be served")
    parser.add_argument('--use_cache', type=int, default=1, help="1 or 0 that determines whether you use cache.csv")
    parser.add_argument('--output_file', type=str, default="us_aws_cdn.csv", help="string that ends in .csv for the output data.")
    parser.add_argument("--company",type=str, default="AMZN", help="generally what company the url serves")
    args = parser.parse_args()

    if args.use_cache == 1:
        dns_server_table = read_cache()
    else:
        dns_server_table = get_public_dns_servers()

    today = date.today().strftime("%m/%d/%Y")
    cdn_providers = {}
    ip_data = {}
    for ip_address in tqdm(dns_server_table['IP Address']):
        cmd = f"dig @{ip_address.split()[0]} {args.url}"
        #print(cmd)
        proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)
        out,err=proc.communicate()
        string_output = out.decode('utf-8')
        string_output_split = string_output.split('ANSWER SECTION')


        if len(string_output_split) > 1:
            filtered_str = string_output_split[1].split('IN	A')[0].split('\n')[-1].split('\t')[0].split(' ')[0]
            if filtered_str in cdn_providers.keys():
                cdn_providers[filtered_str]['usage'] += 1
            else:
                current_series = dns_server_table[dns_server_table["IP Address"] == ip_address]
                cdn_providers[filtered_str] = {
                    'usage':1,
                    'date':today,
                     }
            ip_data[ip_address]={
                    'location':current_series['Location'].iloc[0].split('\n')[0],
                    'reliability':current_series['Reliability'].iloc[0].split('\n')[0],
                    'CDN':filtered_str,
                    'date':today
                    }
            

    cdn_provider_DF = pd.DataFrame(cdn_providers)
    cdn_provider_DF.to_csv(date.today().strftime("%m_%d_%Y")+"_"+args.output_file)
    ip_data = pd.DataFrame(ip_data)
    ip_data.to_csv(date.today().strftime("%m_%d_%Y")+"_"+args.output_file.split('.')[0] + '_vebose.csv')