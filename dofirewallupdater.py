import argparse
import requests
import json
import os.path

parser = argparse.ArgumentParser(description='Update Digital Ocean firewall IP address with your public IP')
parser.add_argument('--firewall-id', help='Digital Ocean Firewall ID', required=True)
parser.add_argument('--api-token', help='Digital Ocean API Token with write permission', required=True)
parser.add_argument('--known-ip-filepath', help='File path to the file storing the known IP address in '
                                                '(default: dofw_last_ipaddr)',
                    default='dofw_last_ipaddr')
args = parser.parse_args()

do_api_token = args.api_token
do_firewall_id = args.firewall_id

last_ip_filename = args.known_ip_filepath

do_firewall_endpoint = "https://api.digitalocean.com/v2/firewalls/{0}"
do_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(do_api_token)}

public_ip_provider = "https://ifconfig.co/ip"
public_ip = requests.get(public_ip_provider).content.strip('\n')

last_known_ip = ''
if os.path.isfile(last_ip_filename):
    last_ip_file = file(last_ip_filename, 'r')
    last_known_ip = last_ip_file.read()
    last_ip_file.close()
else:
    print('Creating file {0} for storing last known IP address'.format(last_ip_filename))
    last_ip_file = file(last_ip_filename, 'w+')
    last_ip_file.close()

if public_ip != last_known_ip:
    print('Updating firewall IP address as {0} (existing) is not equal to {1} (current)'.format(last_known_ip,
                                                                                                public_ip))
    existing_rules_request = requests.get(do_firewall_endpoint.format(do_firewall_id),
                                          headers=do_headers)
    existing_rules_json = existing_rules_request.json()
    existing_rules = existing_rules_json['firewall']
    updated_firewall = {'name': existing_rules['name'], 'inbound_rules': existing_rules['inbound_rules'],
                        'outbound_rules': existing_rules['outbound_rules'],
                        'droplet_ids': existing_rules['droplet_ids'],
                        'tags': existing_rules['tags']}

    for irx, inbound_rule in enumerate(updated_firewall['inbound_rules']):
        if inbound_rule['protocol'] == 'icmp':
            del updated_firewall['inbound_rules'][irx]['ports']
        elif inbound_rule['ports'] == '0':
            updated_firewall['inbound_rules'][irx]['ports'] = 'all'
        for iax, address in enumerate(inbound_rule['sources']['addresses']):
            if address == last_known_ip:
                updated_firewall['inbound_rules'][irx]['sources']['addresses'][iax] = public_ip

    for orx, outbound_rule in enumerate(updated_firewall['outbound_rules']):
        if outbound_rule['protocol'] == 'icmp':
            del updated_firewall['outbound_rules'][orx]['ports']
        elif outbound_rule['ports'] == '0':
            updated_firewall['outbound_rules'][orx]['ports'] = 'all'
        for oax, address in enumerate(outbound_rule['destinations']['addresses']):
            if address == last_known_ip:
                updated_firewall['outbound_rules'][orx]['destinations']['addresses'][oax] = public_ip

    updated_firewall_json = json.dumps(updated_firewall)

    update_request = requests.put(do_firewall_endpoint.format(do_firewall_id), updated_firewall_json,
                                  headers=do_headers)

    if update_request.status_code == 200:
        last_ip_file = file(last_ip_filename, 'w')
        last_ip_file.write(public_ip)
        last_ip_file.close()
        print('Firewall rules and last known IP address updated')

else:
    print('Nothing to update {0} is the existing IP address'.format(last_known_ip))
