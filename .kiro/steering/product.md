# CF Proxy Manager

A Windows desktop tool for managing Cloudflare reverse proxy IP addresses. It helps users find and apply the fastest Cloudflare CDN IP for their proxy domains by:

- Testing TCP connection latency to multiple Cloudflare IPs
- Automatically updating the Windows hosts file with the best IP
- Managing multiple target proxy nodes

The tool is designed for users who need to optimize their connection to Cloudflare-proxied services by selecting optimal edge IPs.

## Primary Use Case

Users configure a CF reverse proxy domain (e.g., `betterclau.de`) and target node (e.g., `anyrouter.top`), then test available Cloudflare IPs to find the lowest latency option. The selected IP is written to the hosts file to bypass DNS and connect directly to the optimal edge server.

## Key Features

- IP speed testing with concurrent TCP connection tests
- Port fallback mechanism (443 → 80) for better connectivity
- Hosts file management (requires admin privileges)
- Hosts file viewer for easy inspection
- Configuration persistence via JSON
- Modern CustomTkinter GUI with dark/light/system themes
- Component-based UI with IP cards showing latency badges
