#!/usr/bin/env python3
"""
Helper: buat file 02_network untuk Ruijie RG-MA3063
Dipanggil dari GitHub Actions workflow saat file belum ada.
"""
import sys
import os
import stat

path = sys.argv[1] if len(sys.argv) > 1 else "02_network"

content = """\
#!/bin/sh
. /lib/functions/uci-defaults.sh

board_config_update

board=$(board_name)
case "$board" in
\truijie,rg-ma3063)
\t\tucidef_set_interfaces_lan_wan "lan1 lan2 lan3" "wan"
\t\t;;
esac

board_config_flush
exit 0
"""

os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
with open(path, "w") as f:
    f.write(content)
os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
print(f"Created: {path}")