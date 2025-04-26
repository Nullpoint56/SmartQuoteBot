# Booting Orange Pi 3B from SATA SSD (SD card + SATA system)

> **Note:** This tutorial is based on the official OrangePi 3B documentation and personal experimentation. It enables booting the **system** from a SATA SSD while keeping the **bootloader** on the SD card.

---

## ✨ Quick Summary

- Follow official documentation ([OrangePi 3B Board Files](https://drive.google.com/drive/folders/18YyPnq_f0gbdNlbsNmzouFPxin08C_gf))
- (Optional) Clear SPI flash memory
- Write SPI flash loader
- Flash Armbian OS to SD card
- Modify `armbianEnv.txt`
- Move system to SATA SSD
- (Important) Do not overwrite bootloader

---

## 🔍 Step-by-Step Instructions

### 1. (Optional) Clear SPI Flash

If you want to start clean:

- Follow "**2.12. Using RKDevTool to clear SPIFlash**" section in the documentation.

### 2. Write Linux Loader to SPI Flash + NVMe (Preparation)

- Follow "**2.6. How to write Linux image to SPIFlash+NVMe SSD**" section.
- **Important:** Select `rk356x_linux_spiflash.cfg` instead of `rk356x_linux_pcie.cfg`.
- When flashing, you only need to select:
  - `MiniLoaderAll.bin`
  - `rkspi_loader.img`
- Follow other instructions as described.

> **Why?** This sets up a minimal SPI loader without PCIe-specific configs.

### 3. Flash Armbian Image to SD Card

- Download Armbian from [Armbian OrangePi 3B page](https://www.armbian.com/orangepi3b/).
- Use [Balena Etcher](https://www.balena.io/etcher/) to flash the image onto your SD card.

### 4. Modify `armbianEnv.txt`

After booting Armbian from SD card:

```bash
sudo nano /boot/armbianEnv.txt
```

At the end of the file, **add:**

```bash
overlays=rk3566-roc-pc-sata2
```

Then save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5. Move System to SATA SSD

Run the Armbian configuration tool:

```bash
sudo armbian-config
```

Navigate:

```
System -> Storage -> Install to internal storage -> Boot from SD card - system on SATA, USB or NVMe
```

- **Important:** When prompted to flash the bootloader at the end, **DO NOT flash it**.
- Exit and reboot.

### 6. Confirm Booting from SATA SSD

Your root filesystem (`/`) should now be located on the SATA SSD, while the bootloader remains on the SD card.

---

## 🚶 Alternative (Untested) Improvement

You could correct `overlay_prefix` for your specific Rockchip SoC inside `armbianEnv.txt` (or via `armbian-config -> System -> Kernel -> Edit the boot environment`).

Then:

- Use `armbian-config -> System -> Kernel -> Manage device tree overlays`
- Enable `roc-pc-sata2` overlay.
- Reboot.

This method may offer a cleaner config but is not fully tested.

---

## ⚠ Important Limitations

- **This method only works for SD card + SATA SSD boot.**
- **It does NOT work for SPI + SATA boot**.
  - **Reason:** OrangePi 3B's default SPI loader (`rkspi_loader.img`) lacks SATA support.
  - To enable SPI + SATA, you would need to build a custom U-Boot image with SATA support.

---

## 📅 Final Recommendation

**Do NOT buy a SATA M.2 SSD for Orange Pi 3B!**

- NVMe drives are **cheaper**, **faster**, and **better supported**.
- I learned the hard way 😅

---

## 📅 Useful Links

- [OrangePi 3B Documentation (Google Drive)](https://drive.google.com/drive/folders/18YyPnq_f0gbdNlbsNmzouFPxin08C_gf)
- [Armbian for OrangePi 3B](https://www.armbian.com/orangepi3b/)
- [Balena Etcher](https://www.balena.io/etcher/)

