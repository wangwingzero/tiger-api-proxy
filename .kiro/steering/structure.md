---
inclusion: always
---

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
    ├── speed_tester.py       # IP latency testing with packet loss detection
    ├── comparison_tester.py  # Proxy comparison testing
    ├── service_manager.py    # Comparison service management
    ├── v2ray_parser.py       # V2Ray link parser (vless/trojan/vmess)
    ├── dns_resolver.py       # DNS resolution utilities
    ├── admin_helper.py       # Admin privilege utilities
    ├── logger.py             # Logging with file output to logs/
    ├── components/           # Reusable UI components
    │   ├── __init__.py
    │   ├── theme.py          # Theme configuration
    │   ├── ip_card.py        # IP card component
    │   ├── comparison_card.py    # Comparison result card
    │   ├── comparison_section.py # Comparison section UI
    │   └── import_dialog.py  # V2Ray import dialog
    └── tests/                # Test suite
        ├── __init__.py
        ├── test_parsers.py
        ├── test_config_manager.py
        ├── test_hosts_manager.py
        ├── test_speed_tester.py
        └── test_comparison.py
```

## Module Responsibilities

| Module | Purpose |
|--------|---------|
| `models.py` | Data structures: `IPEntry`, `TestResult`, `Config`, `ProxyConfig`, `ComparisonService`, `ComparisonResult` |
| `config_manager.py` | JSON config persistence to `config.json` |
| `parsers.py` | `URLParser` and `IPParser` for input validation |
| `hosts_manager.py` | Read/write Windows hosts file, DNS flush |
| `hosts_viewer.py` | Hosts file viewer dialog window |
| `speed_tester.py` | TCP connection latency tests with port fallback and packet loss detection |
| `comparison_tester.py` | HTTPS latency comparison across proxy services |
| `service_manager.py` | Manage comparison service list (add/remove/reset) |
| `v2ray_parser.py` | Parse V2Ray links (vless/trojan/vmess) to extract IPs |
| `dns_resolver.py` | DNS resolution utilities |
| `gui_ctk.py` | Main CustomTkinter GUI application |
| `admin_helper.py` | Admin privilege check utilities |
| `logger.py` | Detailed logging with file output to `logs/` directory |
| `components/theme.py` | Theme colors, fonts, latency thresholds |
| `components/ip_card.py` | IP address card UI component |
| `components/comparison_card.py` | Comparison result card UI component |
| `components/comparison_section.py` | Comparison section with service management |
| `components/import_dialog.py` | V2Ray link import dialog |

## Testing Conventions

- Tests use `hypothesis` for property-based testing
- Test files mirror module names: `test_<module>.py`
- Tests validate requirements documented in docstrings
