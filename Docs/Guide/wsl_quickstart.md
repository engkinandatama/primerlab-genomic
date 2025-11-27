# 🚀 PrimerLab WSL Quickstart Guide

Lupa cara mulai? Ikuti 3 langkah sakti ini setiap kali membuka terminal WSL.

### 1. Buka WSL
Buka aplikasi **Ubuntu** atau terminal **WSL** Anda.

### 2. Masuk ke Folder Project
Project Anda ada di drive E: Windows, yang di-mount ke `/mnt/e`.
```bash
cd /mnt/e/Project/PrimerLab
```

### 3. Aktifkan Virtual Environment (Venv)
Venv Anda tersimpan di home directory Linux (`~`) untuk menghindari masalah permission Windows.
```bash
source ~/primerlab_venv/bin/activate
```
*(Tanda sukses: muncul `(primerlab_venv)` di awal baris terminal)*

---

### 🏁 Siap Eksekusi!
Sekarang Anda bisa menjalankan perintah PrimerLab.

**Contoh PCR:**
```bash
python3 -m primerlab.cli.main run pcr --config test_pcr.yaml
```

**Contoh qPCR:**
```bash
python3 -m primerlab.cli.main run qpcr --config test_qpcr.yaml
```

**Cek Versi:**
```bash
python3 -m primerlab.cli.main version
```
