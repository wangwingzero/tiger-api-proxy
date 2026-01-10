# Project Structure

```
.
├── run.py                    # Launch script (double-click to run)
├── config.json               # User configuration (auto-generated)
├── requirements.txt          # Python dependencies
└── cf_proxy_manager/         # Main package
    ├── __init__.py           # Package init, version
    ├── main.py               # Entry point, admin checks
    ├── gui.py                # Tkinter GUI implementation
    ├── models.py             # Data models (dataclasses)
    ├── config_manager.py     # Config load/save
    ├── parsers.py            # URL/IP parsing
    ├── hosts_manager.py      # Hosts file operations
    ├── speed_tester.py       # IP latency testing
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
| `speed_tester.py` | TCP connection latency tests with threading |
| `gui.py` | Main application window and user interactions |

## Testing Conventions

- Tests use `hypothesis` for property-based testing
- Test files mirror module names: `test_<module>.py`
- Tests validate requirements documented in docstrings
