#!/bin/bash
curl -o - "https://iptoasn.com/data/ip2asn-v4.tsv.gz"  | gunzip  >> ip_asn_db.tsv