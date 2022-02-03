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

# Open Port 9500 to the checking computer IP ONly

`sudo ufw allow from 86.81.155.21 to any port 9500`

# restart Harmony and ufw

```bash
sudo service harmony restart
sudo ufw disable
sudo ufw enable
```
