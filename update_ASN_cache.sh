#!/bin/bash
curl "https://iptoasn.com/data/ip2asn-combined.tsv.gz"  | gunzip  >> ip_asn_db.tsv