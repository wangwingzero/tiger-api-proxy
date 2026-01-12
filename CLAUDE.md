# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tiger API Proxy (虎哥API反代) is a Windows desktop application that optimizes Cloudflare reverse proxy connections by finding the fastest CDN IP through TCP latency testing and automatically updating the Windows hosts file.

**Version:** Defined in `cf_proxy_manager/__init__.py` (single source of truth)

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

# Build EXE (PowerShell)
python -m PyInstaller cf_proxy_manager.spec --noconfirm --clean
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   GUI Layer                      │
│           CFProxyManagerCTk (gui_ctk.py)         │
├─────────────────────────────────────────────────┤
│                Core Services                     │
│  ConfigManager │ SpeedTester │ HostsManager     │
│  URLParser     │ IPParser    │ AdminHelper      │
├─────────────────────────────────────────────────┤
│                 System Layer                     │
│     File I/O  │  Network Socket  │  ctypes      │
└─────────────────────────────────────────────────┘
```

## Key Modules

| Module | Purpose |
|--------|---------|
| `models.py` | Dataclasses: `IPEntry`, `TestResult`, `Config`, `ProxyConfig`, `HostsEntry` |
| `config_manager.py` | JSON config persistence to `config.json` |
| `parsers.py` | `URLParser` and `IPParser` for input validation |
| `hosts_manager.py` | Read/write Windows hosts file, DNS flush, backup |
| `speed_tester.py` | TCP latency tests with port fallback (443→80) |
| `gui_ctk.py` | Main CustomTkinter GUI application |
| `components/theme.py` | Theme colors, fonts, latency thresholds |
| `components/ip_card.py` | Reusable IP card UI component |

## Code Patterns

- **Dataclasses** with `to_dict()`/`from_dict()` for JSON serialization
- **Static methods** for stateless utility functions (parsers)
- **Threading** for non-blocking speed tests (ThreadPoolExecutor, max 5 workers)
- **Port fallback**: Tests port 443 first, falls back to 80 on failure
- **Property-based testing** using `hypothesis` library

## Testing

Tests use `hypothesis` for property-based testing. Test files mirror module names: `test_<module>.py`.

Key correctness properties tested:
1. URL parsing round-trip consistency
2. IP entry parsing consistency
3. Best IP selection (minimum latency among successful results)
4. Failed IP exclusion from best selection
5. Configuration JSON serialization round-trip
6. Hosts entry format correctness

## Version Management

Version is defined in **one place only**: `cf_proxy_manager/__init__.py`

The spec file (`cf_proxy_manager.spec`) automatically reads this version for EXE naming.

## Commit Message Format

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat:` | New feature | MINOR +1 |
| `fix:` | Bug fix | PATCH +1 |
| `perf:` | Performance | PATCH +1 |
| `refactor:`, `docs:`, `test:` | Non-functional | No version change |

## Windows-Specific Notes

- Uses `ctypes.windll` for admin privilege checks
- Hosts file path: `C:\Windows\System32\drivers\etc\hosts`
- Admin privileges recommended for hosts modification
- Build produces single-file EXE with UAC admin request
