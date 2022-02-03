while IFS= read -r block; do
   sudo ufw insert 1 allow from "$block" to any port 9501 comment "$block added to allow list."
done <"blocked.ip.list"
