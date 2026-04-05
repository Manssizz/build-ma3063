# OpenWrt for Ruijie RG-MA3063

> Port OpenWrt ke Ruijie RG-MA3063 — router WiFi 6 AX3000 berbasis Qualcomm IPQ5018.
> Status: **DTS verified, siap build.**

---

## Hardware Specifications

| Komponen | Detail |
|---|---|
| **SoC** | Qualcomm IPQ5000 (IPQ50xx family, compatible IPQ5018) |
| **CPU** | Dual-core ARM Cortex-A53 @ 1.0 GHz |
| **RAM** | 256 MB DDR @ 0x40000000 |
| **Flash** | 128 MB SPI NAND |
| **WiFi 2.4GHz** | IPQ5018 internal radio, 802.11ax 2×2 (ath11k) |
| **WiFi 5GHz** | QCN6122 external radio, 802.11ax 2×2 (ath11k MPD) |
| **Ethernet** | 4× Gigabit RJ45 — 1× WAN + 3× LAN |
| **Switch** | QCA8337 4-port Gigabit |
| **Power** | DC 12V |

---

## Status Verifikasi

| Item | Nilai | Metode Verifikasi |
|---|---|---|
| Layout partisi NAND | 20 partisi, total ~127MB | `/proc/mtd` |
| Target flash OpenWrt | mtd15 `rootfs` @ 0x900000, 50MB | `/proc/mtd` |
| GPIO reset button | GPIO 37, active-low | polling test |
| GPIO switch reset | GPIO 26, active-low | dmesg |
| LED controller | SSDK via QCA8337 | dmesg |
| MAC Address | `48:81:d4:8a:dc:e5` | ART offset `0x0` |
| IPQ5018 caldata | ART offset `0x1000`, 128KB | hexdump |
| QCN6122 caldata | ART offset `0x26800`, 128KB | python3 find |
| IPQ5018 BDF aktif | `bdwlan.b23` (board_id 23) | dmesg `cnss[2]` |
| QCN6122 BDF aktif | `qcn6122/bdwlan.b60` (board_id 60) | dmesg `cnss[41]` |
| WAN port | `eth0` → `dp1`, IPQ5018 internal PHY | confirmed OEM |
| LAN ports | `eth1-3` → `dp2-4`, QCA8337 | confirmed OEM |

---

## Struktur Repository

```
.
├── .github/
│   └── workflows/
│       └── build-openwrt-ma3063.yml   # GitHub Actions build workflow
├── files/
│   ├── dts/
│   │   └── ipq5018-ruijie-rg-ma3063.dts
│   └── firmware/
│       ├── ipq5018/
│       │   └── board.bin              # rename dari bdwlan.b23
│       └── qcn6122/
│           ├── board.bin              # rename dari qcn6122/bdwlan.b60
│           ├── m3_fw.b00
│           ├── m3_fw.b01
│           ├── m3_fw.b02
│           ├── m3_fw.mdt
│           ├── q6_fw.b00 ~ q6_fw.b21
│           └── q6_fw.mdt
└── README.md
```

### Persiapan file firmware (sekali saja)

File BDF dan firmware diambil dari firmware OEM Ruijie yang sudah berjalan di perangkat:

```bash
# Dari router (OEM firmware aktif), jalankan:
mkdir -p /tmp/wfw
mount -t squashfs /tmp/wifi_fw.bin /tmp/wfw

# Dari PC, copy semua:
mkdir -p files/firmware/{ipq5018,qcn6122}

scp root@192.168.10.1:/tmp/wfw/bdwlan.b23      files/firmware/ipq5018/board.bin
scp root@192.168.10.1:/tmp/wfw/qcn6122/bdwlan.b60  files/firmware/qcn6122/board.bin
scp 'root@192.168.10.1:/tmp/wfw/qcn6122/m3_fw.*'   files/firmware/qcn6122/
scp 'root@192.168.10.1:/tmp/wfw/q6_fw.*'           files/firmware/qcn6122/
```

> **Backup ART sebelum apapun:**
> ```bash
> dd if=/dev/mtd13 of=/tmp/art.bin.bak
> scp root@192.168.10.1:/tmp/art.bin.bak ./backup/art_mtd13_backup.bin
> ```

---

## Build via GitHub Actions

Cara paling mudah — tidak perlu setup environment lokal.

1. Fork/push repo ini ke GitHub
2. Pastikan struktur `files/` sudah lengkap (firmware + DTS)
3. Buka tab **Actions** → **Build OpenWrt — Ruijie RG-MA3063**
4. Klik **Run workflow**
5. Tunggu ±60-90 menit (build pertama, toolchain belum cache)
6. Download artifact dari halaman run

> Build kedua dan seterusnya jauh lebih cepat (~20-30 menit) karena toolchain di-cache.

### Output artifacts

| File | Fungsi |
|---|---|
| `*-initramfs-uImage.itb` | Test via TFTP dari U-Boot, **tidak menulis ke flash** |
| `*-sysupgrade.tar` | Flash permanen ke NAND |
| `dotconfig` | `.config` yang dipakai saat build |
| `*.manifest` | Daftar paket yang terinstall |

---

## Build Manual di PC

### 1. Install dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential clang flex bison g++ gawk \
  gcc-multilib g++-multilib gettext git libncurses-dev \
  libssl-dev python3-distutils rsync unzip zlib1g-dev \
  file wget curl libelf-dev quilt
```

### 2. Clone OpenWrt 23.05

```bash
git clone --depth=1 -b openwrt-23.05 \
  https://github.com/openwrt/openwrt.git
cd openwrt
```

### 3. Copy file device

```bash
# DTS
cp ../files/dts/ipq5018-ruijie-rg-ma3063.dts \
   target/linux/qualcommax/files-6.1/arch/arm64/boot/dts/qcom/

# BDF firmware
mkdir -p target/linux/qualcommax/ipq50xx/base-files/lib/firmware/ath11k/{IPQ5018,QCN6122}/hw1.0/

cp ../files/firmware/ipq5018/board.bin \
   target/linux/qualcommax/ipq50xx/base-files/lib/firmware/ath11k/IPQ5018/hw1.0/board.bin

cp ../files/firmware/qcn6122/board.bin \
   target/linux/qualcommax/ipq50xx/base-files/lib/firmware/ath11k/QCN6122/hw1.0/board.bin

cp ../files/firmware/qcn6122/m3_fw.* \
   target/linux/qualcommax/ipq50xx/base-files/lib/firmware/ath11k/QCN6122/hw1.0/

cp ../files/firmware/qcn6122/q6_fw.* \
   target/linux/qualcommax/ipq50xx/base-files/lib/firmware/ath11k/QCN6122/hw1.0/
```

### 4. Apply patches ke OpenWrt tree

**4a. DTS Makefile:**
```bash
DTS_MK="target/linux/qualcommax/files-6.1/arch/arm64/boot/dts/qcom/Makefile"
sed -i '/ipq5018-linksys-mx2000/a dtb-$(CONFIG_ARCH_QCOM) += ipq5018-ruijie-rg-ma3063.dtb' "$DTS_MK"
```

**4b. Device definition — tambahkan ke akhir `target/linux/qualcommax/ipq50xx/Makefile`:**
```makefile
define Device/ruijie_rg-ma3063
  $(call Device/FitImageLzma)
  DEVICE_VENDOR := Ruijie
  DEVICE_MODEL := RG-MA3063
  DEVICE_DTS := qcom/ipq5018-ruijie-rg-ma3063
  DEVICE_DTS_CONFIG := config@mp03.5-c2
  DEVICE_PACKAGES := \
    ath11k-firmware-ipq5018 \
    kmod-ath11k-ahb \
    kmod-ath11k-pci
  SOC := ipq5018
endef
TARGET_DEVICES += ruijie_rg-ma3063
```

**4c. Network board config — tambahkan ke `target/linux/qualcommax/ipq50xx/base-files/etc/board.d/02_network`:**
```bash
# Di dalam blok case $board_name
ruijie,rg-ma3063)
    ucidef_set_interfaces_lan_wan "lan1 lan2 lan3" "wan"
    ;;
```

### 5. Update feeds

```bash
./scripts/feeds update -a
./scripts/feeds install -a
```

### 6. Konfigurasi

```bash
# Gunakan menuconfig
make menuconfig
# Target System → Qualcomm ARM
# Subtarget → IPQ50xx
# Target Profile → Ruijie RG-MA3063

# Atau langsung set via script
cat > .config << 'EOF'
CONFIG_TARGET_qualcommax=y
CONFIG_TARGET_qualcommax_ipq50xx=y
CONFIG_TARGET_qualcommax_ipq50xx_DEVICE_ruijie_rg-ma3063=y
CONFIG_PACKAGE_luci=y
CONFIG_PACKAGE_kmod-ath11k-ahb=y
CONFIG_PACKAGE_kmod-ath11k-pci=y
CONFIG_PACKAGE_ath11k-firmware-ipq5018=y
CONFIG_TARGET_ROOTFS_INITRAMFS=y
EOF

make defconfig
```

### 7. Build

```bash
# Build semua (gunakan semua core)
make -j$(nproc) V=s

# Hasil ada di:
ls -lh bin/targets/qualcommax/ipq50xx/
```

---

## Flashing

> ⚠️ **Selalu test dengan initramfs via TFTP dulu sebelum flash sysupgrade.**
> Initramfs berjalan dari RAM, tidak menyentuh NAND sama sekali.

### Tahap 1 — Test via TFTP (initramfs, aman)

**Setup TFTP server di PC:**
```bash
# Install
sudo apt install tftpd-hpa

# Copy initramfs ke root TFTP
cp openwrt-qualcommax-ipq50xx-ruijie_rg-ma3063-initramfs-uImage.itb /srv/tftp/openwrt-initramfs.itb

# Set IP statis PC ke 192.168.1.2
sudo ip addr add 192.168.1.2/24 dev eth0
```

**Di U-Boot (akses serial 115200 baud):**
```
# Interrupt boot dengan tekan key saat "Hit any key"
setenv ipaddr 192.168.1.1
setenv serverip 192.168.1.2
tftpboot 0x44000000 openwrt-initramfs.itb
bootm 0x44000000
```

Kalau OpenWrt booting dan WiFi/LAN bekerja → lanjut ke flash permanen.

### Tahap 2 — Flash sysupgrade (permanen)

```bash
# Dari OpenWrt yang sudah berjalan (initramfs atau existing)
# Upload sysupgrade ke router
scp openwrt-*-sysupgrade.tar root@192.168.1.1:/tmp/

# Flash
ssh root@192.168.1.1
sysupgrade -v /tmp/openwrt-*-sysupgrade.tar
```

### Layout partisi NAND (referensi)

| mtd | Label | Offset | Ukuran | Keterangan |
|---|---|---|---|---|
| 0 | 0:SBL1 | 0x0000000 | 512KB | Secondary Bootloader |
| 1 | 0:MIBIB | 0x0080000 | 512KB | SMEM Partition Table |
| 2 | 0:BOOTCONFIG | 0x0100000 | 256KB | Boot Config A |
| 3 | 0:BOOTCONFIG1 | 0x0140000 | 256KB | Boot Config B |
| 4 | 0:QSEE | 0x0180000 | 1MB | TrustZone A |
| 5 | 0:QSEE_1 | 0x0280000 | 1MB | TrustZone B |
| 6 | 0:DEVCFG | 0x0380000 | 256KB | Device Config A |
| 7 | 0:DEVCFG_1 | 0x03c0000 | 256KB | Device Config B |
| 8 | 0:CDT | 0x0400000 | 256KB | Clock & DDR Config A |
| 9 | 0:CDT_1 | 0x0440000 | 256KB | Clock & DDR Config B |
| 10 | 0:APPSBLENV | 0x0480000 | 512KB | U-Boot Environment |
| 11 | 0:APPSBL | 0x0500000 | 1.25MB | U-Boot A |
| 12 | 0:APPSBL_1 | 0x0640000 | 1.25MB | U-Boot B |
| **13** | **0:ART** | **0x0780000** | **1MB** | **WiFi Cal + MAC ⚠ jangan ditulis** |
| 14 | 0:TRAINING | 0x0880000 | 512KB | NAND Training |
| **15** | **rootfs** | **0x0900000** | **50MB** | **← Target OpenWrt** |
| 16 | rootfs_1 | 0x3b00000 | 50MB | Backup / A-B update |
| 17 | ttyMTD | 0x6d00000 | 1.1MB | Misc Ruijie |
| 18 | productinfo | 0x6e20000 | 512KB | Info produk (SN, model) |
| 19 | data | 0x6ea0000 | 16.25MB | Persistent data |

---

## Catatan Penting

### ART Partition (mtd13) — JANGAN ditulis ulang
```
Offset 0x0000  : MAC ETH/WAN (48:81:d4:8a:dc:e5)
Offset 0x0006  : MAC WiFi 2.4GHz (sama dengan ETH di OEM)
Offset 0x1000  : IPQ5018 caldata (128KB)
Offset 0x26800 : QCN6122 caldata (128KB)
```

### LED
LED dikontrol oleh SSDK via QCA8337, **bukan** `gpio-leds` biasa.
- dmesg: `ssdk_led_mode:3, ssdk_led_map:0xffc, ssdk_led_src_id:0`
- 6 LED fisik: `led1_{blue,green,red}` dan `led2_{blue,green,red}`
- Konfigurasi trigger via LuCI → System → LED Configuration

### Serial Console
- **Baud:** 115200 8N1
- **Pin:** cari pad UART di PCB (TX, RX, GND)
- DTS: `stdout-path = "serial0:115200n8"`

---

## Referensi

- [OpenWrt IPQ50xx support PR #17182](https://github.com/openwrt/openwrt/pull/17182)
- [Linksys MX2000 DTS (referensi IPQ5018)](https://github.com/openwrt/openwrt/blob/main/target/linux/qualcommax/files-6.1/arch/arm64/boot/dts/qcom/ipq5018-linksys-mx2000.dts)
- [ath11k firmware repository](https://github.com/kvalo/ath11k-firmware)
- [OpenWrt qualcommax target](https://github.com/openwrt/openwrt/tree/main/target/linux/qualcommax)
