# Asyncio Port Scanner (Python)

A small, Linux-friendly **asyncio** TCP port scanner that reads targets from a file and generates **JSON + CSV** reports.

> **Legal / Safety notice:** Scan only systems you own or where you have explicit permission.

---

## Features

- Async TCP connect scanning with a global concurrency limit (`--concurrency`)
- Per-port timeout (`--timeout`)
- Targets from a text file (IP or domain)
- DNS resolution for domain targets
- Reports:
  - `*.json` (full structured output + metadata)
  - `*.csv` (quick spreadsheet-friendly format)

---

## Requirements

- Python **3.8+** (stdlib only; no external dependencies)

---

## Setup (venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

---

## Usage

### 1) Create a targets file

`targets.txt` (one target per line):

```txt
8.8.8.8
example.com
192.168.1.1
```

### 2) Run the scanner

```bash
python3 portscan.py -i targets.txt -o scan_report
```

This will create:

- `scan_report.json`
- `scan_report.csv`

---

## Options

- `-i, --input` : input file containing targets (required)
- `-o, --out` : output prefix (default: `report`)
- `--ports` : comma-separated ports
  - default: a curated list of common ports
  - example: `--ports 22,80,443,8080`
- `--timeout` : timeout per port in seconds (default: `0.8`)
- `--concurrency` : maximum simultaneous connections (default: `400`)

Example with custom ports:

```bash
python3 portscan.py -i targets.txt -o scan_report --ports 22,80,443 --timeout 1.2 --concurrency 300
```

---

## Output format

### JSON (`*.json`)

Contains:

- `meta`: started/finished timestamps, ports, timeout, concurrency
- `results`: list of targets with resolved IP and `open_ports`

### CSV (`*.csv`)

Columns:

- `target`
- `ip`
- `open_ports` (semicolon-separated)
- `error`

---

## License

MIT — see [LICENSE](./LICENSE).

---

# ماسح منافذ Asyncio (بايثون)

سكريبت بسيط **asyncio** لفحص منافذ TCP، يقرأ الأهداف من ملف ويُخرج تقريرين **JSON + CSV**.

> **تنبيه قانوني / أمني:** افحص فقط الأنظمة التي تملكها أو لديك إذن صريح لفحصها.

---

## المميزات

- فحص TCP (connect) بشكل غير متزامن مع حد أعلى للتوازي (`--concurrency`)
- مهلة لكل منفذ (`--timeout`)
- قراءة الأهداف من ملف نصي (IP أو Domain)
- حل DNS للدومينات
- تقارير:
  - `*.json` تقرير كامل مع بيانات وصفية
  - `*.csv` تقرير بسيط مناسب للإكسل

---

## المتطلبات

- Python **3.8+** (بدون مكتبات خارجية)

---

## الإعداد (بيئة افتراضية venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

---

## التشغيل

### 1) أنشئ ملف الأهداف

ملف `targets.txt` (هدف واحد في كل سطر):

```txt
8.8.8.8
example.com
192.168.1.1
```

### 2) شغل الأداة

```bash
python3 portscan.py -i targets.txt -o scan_report
```

سيتم إنشاء:

- `scan_report.json`
- `scan_report.csv`

---

## الخيارات

- `-i, --input` ملف الأهداف (إجباري)
- `-o, --out` اسم/بادئة ملفات الإخراج (الافتراضي: `report`)
- `--ports` منافذ مفصولة بفاصلة
  - مثال: `--ports 22,80,443,8080`
- `--timeout` المهلة لكل منفذ بالثواني (الافتراضي: `0.8`)
- `--concurrency` أقصى عدد اتصالات متزامنة (الافتراضي: `400`)

مثال تشغيل مع منافذ مخصصة:

```bash
python3 portscan.py -i targets.txt -o scan_report --ports 22,80,443 --timeout 1.2 --concurrency 300
```

---

## الرخصة

MIT — راجع ملف [LICENSE](./LICENSE).
