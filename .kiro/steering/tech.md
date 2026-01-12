---
inclusion: always
---

# Tech Stack

## Language & Runtime

- Python 3.x
- Windows-specific (uses `ctypes.windll` for admin checks, Windows hosts path)

## GUI Framework

- CustomTkinter (modern themed Tkinter wrapper)
- Supports dark/light/system theme modes

## Dependencies

- `hypothesis>=6.0.0` - Property-based testing
- `pytest>=7.0.0` - Test framework
- `customtkinter>=5.2.0` - Modern GUI framework

## Project Structure

```
cf_proxy_manager/     # Main package
├── main.py           # Entry point, admin privilege handling
├── gui_ctk.py        # CustomTkinter GUI (CFProxyManagerCTk class)
├── models.py         # Dataclasses: IPEntry, TestResult, Config, ProxyConfig, ComparisonService, ComparisonResult
├── config_manager.py # JSON config persistence
├── parsers.py        # URL and IP parsing utilities
├── hosts_manager.py  # Windows hosts file operations
├── hosts_viewer.py   # Hosts file viewer dialog
├── speed_tester.py   # TCP latency testing with port fallback (443→80) and packet loss detection
├── comparison_tester.py  # HTTPS latency comparison across proxy services
├── service_manager.py    # Comparison service list management
├── admin_helper.py   # Admin privilege utilities
├── logger.py         # Detailed logging with file output
├── components/       # Reusable UI components
│   ├── theme.py      # Theme configuration
│   ├── ip_card.py    # IP card component
│   ├── comparison_card.py    # Comparison result card
│   └── comparison_section.py # Comparison section UI
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
- Component-based UI architecture
