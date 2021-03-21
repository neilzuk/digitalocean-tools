import argparse
import requests
import json
import socket
import datetime as dt

parser = argparse.ArgumentParser(description='Update Digital Ocean firewall IP address with your public IP')
parser.add_argument('--firewall-id', help='Digital Ocean Firewall ID', required=True)
parser.add_argument('--api-token', help='Digital Ocean API Token with write permission', required=True)
parser.add_argument('--config', help='File path to the file storing the config'
                                     '(default: config.json)',
                    default='config.json')
args = parser.parse_args()

config_filename = args.config

do_api_token = args.api_token
do_firewall_id = args.firewall_id
do_firewall_endpoint = "https://api.digitalocean.com/v2/firewalls/{0}"
do_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(do_api_token)}

with open(config_filename, 'r+') as config_json_file:
    config_data = json.load(config_json_file)
    old_to_new_ip_map = {}
    for endpoint in config_data['endpoints']:
        last_endpoint_ip = endpoint['lastIP']
        resolved_endpoint_ip = socket.gethostbyname(endpoint['host'])
        if last_endpoint_ip != resolved_endpoint_ip:
            print("Host: {0} was '{1}' is now '{2}'".format(endpoint['host'], last_endpoint_ip, resolved_endpoint_ip))
            old_to_new_ip_map[last_endpoint_ip] = resolved_endpoint_ip
            endpoint['lastIP'] = resolved_endpoint_ip
            endpoint['lastUpdated'] = dt.datetime.now(dt.timezone.utc).isoformat()

    if len(old_to_new_ip_map) > 0:
        print("Firewall update is required...fetching existing rules from provider")
        existing_rules_request = requests.get(do_firewall_endpoint.format(do_firewall_id),
                                              headers=do_headers)

        if existing_rules_request.status_code == 200:
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
                    if new_ip := old_to_new_ip_map.get(address):
                        updated_firewall['inbound_rules'][irx]['sources']['addresses'][iax] = new_ip

            for orx, outbound_rule in enumerate(updated_firewall['outbound_rules']):
                if outbound_rule['protocol'] == 'icmp':
                    del updated_firewall['outbound_rules'][orx]['ports']
                elif outbound_rule['ports'] == '0':
                    updated_firewall['outbound_rules'][orx]['ports'] = 'all'
                for oax, address in enumerate(outbound_rule['destinations']['addresses']):
                    if new_ip := old_to_new_ip_map.get(address):
                        updated_firewall['outbound_rules'][orx]['destinations']['addresses'][oax] = new_ip

            updated_firewall_json = json.dumps(updated_firewall)

            update_request = requests.put(do_firewall_endpoint.format(do_firewall_id), updated_firewall_json,
                                          headers=do_headers)

            if update_request.status_code == 200:
                print('Firewall rules updated')
                config_json_file.seek(0)
                json.dump(config_data, config_json_file, indent=2)
                config_json_file.truncate()
                print('Config file updated')
            else:
                print('Firewall could not be updated')
                print(update_request.content)
                exit(1)
        else:
            print('Could not get existing firewall')
            print(existing_rules_request.content)
            exit(1)
    else:
        print("No firewall updates required.")
        exit(0)
