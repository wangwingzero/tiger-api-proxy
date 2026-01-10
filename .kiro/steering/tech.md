# Tech Stack

## Language & Runtime

- Python 3.x
- Windows-specific (uses `ctypes.windll` for admin checks, Windows hosts path)

## GUI Framework

- Tkinter (standard library) with ttk widgets

## Dependencies

- `hypothesis>=6.0.0` - Property-based testing
- `pytest>=7.0.0` - Test framework

## Project Structure

```
cf_proxy_manager/     # Main package
├── main.py           # Entry point, admin privilege handling
├── gui.py            # Tkinter GUI (CFProxyManagerGUI class)
├── models.py         # Dataclasses: IPEntry, TestResult, Config, ProxyConfig
├── config_manager.py # JSON config persistence
├── parsers.py        # URL and IP parsing utilities
├── hosts_manager.py  # Windows hosts file operations
├── speed_tester.py   # TCP latency testing with ThreadPoolExecutor
└── tests/            # Property-based tests using hypothesis
```

## Common Commands

```bash
# Run the application
python run.py

# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest cf_proxy_manager/tests/test_parsers.py
```

## Code Patterns

- Dataclasses with `to_dict()`/`from_dict()` for serialization
- Static methods for stateless utility functions
- Threading for non-blocking speed tests
- Regex patterns for IP and hosts file parsing
