import shlex
import subprocess
import netaddr
import pandas as pd

if __name__ == '__main__':
    subprocess.Popen(shlex.split('./update_ASN_cache.sh'))

    print('downloaded ASN DB')

    asn_db = pd.read_csv(
        'ip_asn_db.tsv',
        names="range_start range_end AS_number country_code AS_description".split(
            ' '),
        delimiter='\t'
    )
    cidr_numeric = asn_db.apply(lambda x: netaddr.iprange_to_cidrs(
        x.range_start, x.range_end), axis=1)

    cidr_str = cidr_numeric.map(lambda x: list(map(str, x)))
    asn_db['cidr_block'] = cidr_str
    asn_db.to_csv('asn_db.csv')