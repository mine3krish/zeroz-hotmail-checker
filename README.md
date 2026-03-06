# ZEROZ Hotmail Checker

> Fast, multi-threaded Hotmail / Outlook account checker with a modern dark GUI.

**Free & Open Source** -- built with Python and customtkinter.

---

> **Looking for the EXE build, Premium version, or latest releases?**
> Join the Telegram channel for downloads and updates:
>
> [![Download on Telegram](https://img.shields.io/badge/Download_Latest-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/zerozpanel)

---

## Features

- **Multi-threaded checking** -- configurable thread count (1-100) for fast batch processing.
- **Proxy support** -- single proxy, or rotate through a proxy list automatically.
- **OWA token verification** -- goes beyond login to confirm inbox access and count.
- **2FA detection** -- identifies accounts with two-factor authentication enabled.
- **Modern dark UI** -- polished interface with stat cards, progress bar, tabbed results.
- **Live stats** -- real-time CPM (checks per minute), progress percentage, per-category counters.
- **Filter & search** -- filter results in real-time from the results tab.
- **Export** -- export good hits to `.txt` with checkbox selection.
- **Copy to clipboard** -- bulk copy selected accounts instantly.

## Result Categories

| Status    | Meaning                                       |
|-----------|-----------------------------------------------|
| **GOOD**  | Login successful, inbox access confirmed      |
| **2FA**   | Login OK but two-factor authentication active |
| **BAD**   | Incorrect password                            |
| **INVALID** | Account does not exist                      |
| **LOCKED** | Account suspended / blocked                  |
| **ERROR** | Network or parsing error (retried)            |

## Installation

**Requirements:** Python 3.9+

```bash
# Clone the repository
git clone https://github.com/mine3krish/zeroz-hotmail-checker
cd zeroz-hotmail-checker

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package          | Purpose                               |
|------------------|---------------------------------------|
| `curl_cffi`      | TLS-fingerprint-aware HTTP client     |
| `customtkinter`  | Modern themed tkinter widgets         |

## Usage

```bash
# Option 1: Run the launcher
python run.py

# Option 2: Run as a module
python -m zeroz
```

### Quick Start

1. Launch the app.
2. Click **Load Combo** and select a `.txt` file with `email:password` lines.
3. (Optional) Enter a proxy or load a proxy list.
4. Adjust **Threads**, **Timeout**, and **Retries** with the sliders.
5. Click **START**.
6. Watch results populate in real-time across the tabs.
7. Use the **Good Hits** tab to select and **Export** or **Copy** accounts.

### Combo Format

One account per line:

```
user@hotmail.com:password123
another@outlook.com:mypassword
```

### Proxy Format

One proxy per line (HTTP):

```
host:port
user:pass@host:port
```

## Project Structure

```
zeroz-hotmail-checker/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── run.py                 # Quick launcher
└── zeroz/
    ├── __init__.py        # Package version
    ├── __main__.py        # python -m zeroz entry point
    ├── checker.py         # Core login engine (no GUI)
    ├── app.py             # Main GUI application
    ├── theme.py           # Colors, fonts, styling
    └── widgets.py         # Reusable UI components
```

## Community

Join the Telegram channel for updates, support, and discussion:

[![Telegram](https://img.shields.io/badge/Telegram-COSMO%20UNION-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/zerozpanel)

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request.

Please keep code clean, follow the existing style, and test your changes before submitting.

## License

This project is licensed under the [MIT License](LICENSE).

---

**ZEROZ** -- Free & Open Source | [Telegram](https://t.me/zerozpanel)
