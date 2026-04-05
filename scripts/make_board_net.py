#!/usr/bin/env python3
"""
Buat file 02_network untuk Ruijie RG-MA3063.
Pakai struktur OpenWrt 25.12 (fungsi ipq50xx_setup_interfaces).
Dipanggil dari GitHub Actions workflow saat file belum ada di tree.
"""
import sys
import os
import stat

path = sys.argv[1] if len(sys.argv) > 1 else "02_network"

content = """\
#!/bin/sh
. /lib/functions/uci-defaults.sh

ipq50xx_setup_interfaces()
{
\tlocal board="$1"

\tcase $board in
\truijie,rg-ma3063)
\t\tucidef_set_interfaces_lan_wan "lan1 lan2 lan3" "wan"
\t\t;;
\tesac
}

board_config_update

board=$(board_name)
ipq50xx_setup_interfaces "$board"

board_config_flush
exit 0
"""

os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
with open(path, "w") as f:
    f.write(content)
os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
print(f"✅ Created: {path}")
