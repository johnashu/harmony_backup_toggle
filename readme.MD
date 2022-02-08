# Harmony Redundancy Monitor / Updater

An Async service written in Python that will monitor Validator nodes to ensure that only 1 of them will be signing at any given moment.

If a node is uncontactable, then the program will turn on the backup node and switch to signing. If the original signing node recovers by itself, it will turn the flag off.


# install

`sudo apt update && sudo apt upgrade -y`

`apt install python3-pip`

`pip3 install -r requirements.txt`

# expose http port in harmony.conf

```bash
[HTTP]
  AuthPort = 9501
  Enabled = true
 ** IP = "0.0.0.0"**
  Port = 9500
  RosettaEnabled = false
  RosettaPort = 9700
```

# Open Port 9501 to the checking computer IP ONly

`sudo ufw allow from 86.81.155.21 to any port 9501`

for multiple IPs

`sudo nano allow.ip.list`

Update the file with a list of IPs. Alternatively upload the file to the node.

```bash
>>> allow.ip.list

123.456.0.1
987.654.321.1
...

```

# run update script

> ./scripts/update_ufw.sh

`sudo bash update_ufw.sh`

or create the file manually..

```bash
while IFS= read -r allow; do
   sudo ufw insert 1 allow from "$allow" to any port 9501 comment "$allow known redundancy monitoring service"
done <"allow.ip.list"

```

# restart Harmony and ufw

```bash
sudo service harmony restart
sudo ufw disable
sudo ufw enable
```

Create CSV file (comma seperated) with the following info (No Header)

Signer IP  |  Signer Nickname  | BackUp IP  |  BackUp NickName
154.53.50.54,66.94.122.253


curl --location --request POST 'http://66.94.122.253:9501/' --header 'Content-Type: application/json' --data-raw '{"jsonrpc": "2.0","method" : "hmy_getNodeMetadata","params": [],"id": 1}' | jq
# restart instance Contabo
https://api.contabo.com/#operation/restart