# Project Structure

```
.
├── run.py                    # Launch script (double-click to run)
├── config.json               # User configuration (auto-generated)
├── requirements.txt          # Python dependencies
└── cf_proxy_manager/         # Main package
    ├── __init__.py           # Package init, version
    ├── main.py               # Entry point, admin checks
    ├── gui.py                # Legacy Tkinter GUI (deprecated)
    ├── gui_ctk.py            # CustomTkinter GUI (main)
    ├── models.py             # Data models (dataclasses)
    ├── config_manager.py     # Config load/save
    ├── parsers.py            # URL/IP parsing
    ├── hosts_manager.py      # Hosts file operations
    ├── hosts_viewer.py       # Hosts file viewer dialog
    ├── speed_tester.py       # IP latency testing
    ├── admin_helper.py       # Admin privilege utilities
    ├── components/           # Reusable UI components
    │   ├── __init__.py
    │   ├── theme.py          # Theme configuration
    │   └── ip_card.py        # IP card component
    └── tests/                # Test suite
        ├── __init__.py
        ├── test_parsers.py
        ├── test_config_manager.py
        ├── test_hosts_manager.py
        └── test_speed_tester.py
```

## Module Responsibilities

| Module | Purpose |
|--------|---------|
| `models.py` | Data structures: `IPEntry`, `TestResult`, `Config`, `ProxyConfig` |
| `config_manager.py` | JSON config persistence to `config.json` |
| `parsers.py` | `URLParser` and `IPParser` for input validation |
| `hosts_manager.py` | Read/write Windows hosts file, DNS flush |
| `hosts_viewer.py` | Hosts file viewer dialog window |
| `speed_tester.py` | TCP connection latency tests with port fallback |
| `gui_ctk.py` | Main CustomTkinter GUI application |
| `admin_helper.py` | Admin privilege check utilities |
| `components/theme.py` | Theme colors, fonts, latency thresholds |
| `components/ip_card.py` | IP address card UI component |

## Testing Conventions

- Tests use `hypothesis` for property-based testing
- Test files mirror module names: `test_<module>.py`
- Tests validate requirements documented in docstrings
