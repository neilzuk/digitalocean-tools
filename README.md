# Digital Ocean Firewall Updater
This Python script was created to update my Digital Ocean firewall rules when ISP dynamic IP address changes.
 It fetches the firewall rules using the DO API and replaces the old DHCP IP address with your new one from a defined DDNS, storing this known 
 IP in a file for a simple comparison. The idea is that this script is run frequently from a device such as a Raspberry Pi 
 that is online 24/7 to maintain access to DO resources that are firewalled off.  
  
 ## Requirements
 * **Note:** Your firewall must already be setup with your existing public IP address
 * Python 3.8+  
 * Install the **requests** library using `pip3 install requests` from your command line
 
 ## Usage
 ```
usage: dofirewallupdater.py [-h] --firewall-id FIREWALL_ID --api-token API_TOKEN [--config CONFIG]

Update Digital Ocean firewall IP address with your public IP

optional arguments:
  -h, --help            show this help message and exit
  --firewall-id FIREWALL_ID
                        Digital Ocean Firewall ID
  --api-token API_TOKEN
                        Digital Ocean API Token with write permission
  --config CONFIG       File path to the file storing the config(default: config.json)
```
### Config.json
Rename the config.sample.json file to config.json and set your DDNS providers hostname and your current IP.

### Automatic updates using crontab 
To run the updater every 5 minutes add the following to your crontab with your own Firewall ID and API token 
```
*/5 * * * * python3 /home/pi/digitalocean/dofirewallupdater.py --firewall-id XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX --api-token XXXXXXXXXXXXX 2>/dev/null
```
