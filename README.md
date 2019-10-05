# Digital Ocean Firewall Updater
This Python script was created to update my Digital Ocean firewall rules when ISP dynamic IP address changes.
 It fetches the firewall rules using the DO API and replaces the old DHCP IP address with your new one, storing this known 
 IP in a file for a simple comparison. The idea is that this script is run frequently from a device such as a Raspberry Pi 
 that is online 24/7 to maintain access to DO resources that are firewalled off.  
 
 The script uses https://ifconfig.co to determine your public facing IP address.
 
 ## Requirements
 * **Note:** Your firewall must already be setup with your existing public IP address
 * Python 3  
 * Install the **requests** library using `pip3 install requests` from your command line
 
 ## Usage
 ```
usage: dofirewallupdater.py [-h] --firewall-id FIREWALL_ID --api-token
                            API_TOKEN [--known-ip-filepath KNOWN_IP_FILEPATH]

Update Digital Ocean firewall IP address with your public IP

optional arguments:
  -h, --help            show this help message and exit
  --firewall-id FIREWALL_ID
                        Digital Ocean Firewall ID
  --api-token API_TOKEN
                        Digital Ocean API Token with write permission
  --known-ip-filepath KNOWN_IP_FILEPATH
                        File path to the file storing the known IP address in
                        (default: dofw_last_ipaddr)
```

### Automatic updates using crontab 
To run the updater every 5 minutes add the following to your crontab with your own Firewall ID and API token 
```
*/5 * * * * python3 /home/pi/digitalocean/dofirewallupdater.py --firewall-id XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX --api-token XXXXXXXXXXXXX 2>/dev/null
```
