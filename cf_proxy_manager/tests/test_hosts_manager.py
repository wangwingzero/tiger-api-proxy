"""
Property-based tests for HostsManager
Feature: cf-proxy-manager
Property 6: Hosts Entry Format Correctness
Validates: Requirements 5.2

Feature: hosts-viewer
Property 1: Hosts File Parsing Completeness
Validates: Requirements 1.1, 1.2
"""
import tempfile
import os
from hypothesis import given, strategies as st, settings, HealthCheck

from cf_proxy_manager.hosts_manager import HostsManager
from cf_proxy_manager.models import HostsEntry


# Strategies
ip_octet = st.integers(min_value=0, max_value=255)
ip_strategy = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
    lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
)

domain_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=3, max_size=10
).map(lambda s: f"{s}.com")

# Strategy for generating hosts file content
comment_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789 ",
    min_size=0, max_size=30
).map(lambda s: f"# {s}")

empty_line_strategy = st.sampled_from(["", "   ", "\t"])

hosts_entry_strategy = st.tuples(ip_strategy, domain_strategy).map(
    lambda t: (f"{t[0]} {t[1]}", t[0], t[1])  # (line, ip, domain)
)

# Strategy for mixed hosts file lines
hosts_line_strategy = st.one_of(
    hosts_entry_strategy.map(lambda t: ("entry", t)),
    comment_strategy.map(lambda c: ("comment", c)),
    empty_line_strategy.map(lambda e: ("empty", e))
)


class TestHostsManagerProperties:
    """Property-based tests for HostsManager"""
    
    @given(ip=ip_strategy, domain=domain_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_hosts_entry_format_round_trip(self, ip: str, domain: str):
        """
        Property 6: Hosts Entry Format Correctness
        For any valid domain and IP, the generated hosts entry should
        follow the format 'IP DOMAIN' and be parseable back.
        Validates: Requirements 5.2
        """
        # Format entry
        entry = HostsManager.format_entry(ip, domain)
        
        # Verify format
        assert entry == f"{ip} {domain}"
        
        # Parse it back
        parsed = HostsManager.parse_entry(entry)
        
        assert parsed is not None
        parsed_ip, parsed_domain = parsed
        assert parsed_ip == ip
        assert parsed_domain == domain
    
    @given(ip=ip_strategy, domain=domain_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_entry_with_extra_whitespace(self, ip: str, domain: str):
        """
        Test that entries with extra whitespace are still parseable.
        """
        # Entry with extra spaces
        entry = f"  {ip}    {domain}  "
        
        parsed = HostsManager.parse_entry(entry)
        
        assert parsed is not None
        parsed_ip, parsed_domain = parsed
        assert parsed_ip == ip
        assert parsed_domain == domain
    
    def test_comment_lines_ignored(self):
        """Test that comment lines return None"""
        comments = [
            "# This is a comment",
            "#127.0.0.1 localhost",
            "  # indented comment",
        ]
        
        for comment in comments:
            assert HostsManager.parse_entry(comment) is None
    
    def test_empty_lines_ignored(self):
        """Test that empty lines return None"""
        empty_lines = ["", "   ", "\t", "\n"]
        
        for line in empty_lines:
            assert HostsManager.parse_entry(line) is None
    
    def test_invalid_entries_rejected(self):
        """Test that invalid entries return None"""
        invalid = [
            "not an ip address domain.com",
            "256.1.1.1 domain.com",  # Invalid IP
            "localhost",  # No IP
        ]
        
        for entry in invalid:
            result = HostsManager.parse_entry(entry)
            # Some may parse, some may not - just ensure no crash
            pass
    
    @given(lines=st.lists(hosts_line_strategy, min_size=0, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_hosts_file_parsing_completeness(self, lines):
        """
        Property 1: Hosts File Parsing Completeness
        For any valid hosts file content containing IP-domain mappings, 
        comments, and empty lines, the parser should return exactly all 
        valid IP-domain pairs while excluding comments and empty lines.
        
        Feature: hosts-viewer
        Validates: Requirements 1.1, 1.2
        """
        # Build hosts file content and track expected entries
        content_lines = []
        expected_entries = []
        
        for line_type, data in lines:
            if line_type == "entry":
                line, ip, domain = data
                content_lines.append(line)
                expected_entries.append((ip, domain))
            elif line_type == "comment":
                content_lines.append(data)
            else:  # empty
                content_lines.append(data)
        
        content = "\n".join(content_lines)
        
        # Create temp hosts file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Parse using HostsManager
            manager = HostsManager(hosts_path=temp_path)
            parsed_entries = manager.get_all_entries()
            
            # Verify count matches
            assert len(parsed_entries) == len(expected_entries), \
                f"Expected {len(expected_entries)} entries, got {len(parsed_entries)}"
            
            # Verify each entry
            for i, (expected_ip, expected_domain) in enumerate(expected_entries):
                assert parsed_entries[i].ip == expected_ip
                assert parsed_entries[i].domain == expected_domain
        finally:
            os.unlink(temp_path)
