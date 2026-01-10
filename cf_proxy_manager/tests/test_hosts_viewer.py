"""
Property-based tests for Hosts Viewer
Feature: hosts-viewer
Property 3: Search Filter Accuracy
Validates: Requirements 4.2
"""
import tempfile
import os
from hypothesis import given, strategies as st, settings, HealthCheck

from cf_proxy_manager.hosts_manager import HostsManager
from cf_proxy_manager.models import HostsEntry
from cf_proxy_manager.hosts_viewer import is_localhost_entry, LOCALHOST_IPS


# Strategies
ip_octet = st.integers(min_value=0, max_value=255)
ip_strategy = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
    lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
)

domain_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=3, max_size=10
).map(lambda s: f"{s}.com")

hosts_entry_strategy = st.builds(
    HostsEntry,
    ip=ip_strategy,
    domain=domain_strategy
)

# Search query strategy - can be part of IP or domain
search_query_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789.",
    min_size=1, max_size=5
)


class TestHostsViewerProperties:
    """Property-based tests for Hosts Viewer search functionality"""
    
    @given(
        entries=st.lists(hosts_entry_strategy, min_size=1, max_size=20),
        query=search_query_strategy
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_search_filter_accuracy(self, entries, query):
        """
        Property 3: Search Filter Accuracy
        For any list of hosts entries and any search query, all returned 
        entries should contain the query string in either the domain or 
        IP field (case-insensitive).
        
        Feature: hosts-viewer
        Validates: Requirements 4.2
        """
        # Filter entries using the matches method
        filtered = [e for e in entries if e.matches(query)]
        
        # Verify all filtered entries contain the query
        query_lower = query.lower()
        for entry in filtered:
            assert query_lower in entry.domain.lower() or query_lower in entry.ip.lower(), \
                f"Entry {entry} does not match query '{query}'"
        
        # Verify no matching entries were excluded
        for entry in entries:
            if entry not in filtered:
                assert query_lower not in entry.domain.lower() and query_lower not in entry.ip.lower(), \
                    f"Entry {entry} should have matched query '{query}'"
    
    @given(entries=st.lists(hosts_entry_strategy, min_size=0, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_empty_query_returns_all(self, entries):
        """
        Test that empty query returns all entries.
        """
        filtered = [e for e in entries if e.matches("")]
        assert len(filtered) == len(entries)
    
    @given(entry=hosts_entry_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_exact_domain_match(self, entry):
        """
        Test that searching for exact domain always matches.
        """
        assert entry.matches(entry.domain)
    
    @given(entry=hosts_entry_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_exact_ip_match(self, entry):
        """
        Test that searching for exact IP always matches.
        """
        assert entry.matches(entry.ip)
    
    @given(entry=hosts_entry_strategy, query=search_query_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_case_insensitive_search(self, entry, query):
        """
        Test that search is case-insensitive.
        """
        result_lower = entry.matches(query.lower())
        result_upper = entry.matches(query.upper())
        result_mixed = entry.matches(query.title())
        
        # All case variations should give same result
        assert result_lower == result_upper == result_mixed


class TestHostsEntryModel:
    """Unit tests for HostsEntry model"""
    
    def test_matches_domain_substring(self):
        """Test matching domain substring"""
        entry = HostsEntry(ip="192.168.1.1", domain="example.com")
        assert entry.matches("example")
        assert entry.matches("exam")
        assert entry.matches(".com")
    
    def test_matches_ip_substring(self):
        """Test matching IP substring"""
        entry = HostsEntry(ip="192.168.1.1", domain="example.com")
        assert entry.matches("192")
        assert entry.matches("168")
        assert entry.matches("192.168")
    
    def test_no_match(self):
        """Test non-matching query"""
        entry = HostsEntry(ip="192.168.1.1", domain="example.com")
        assert not entry.matches("google")
        assert not entry.matches("10.0")
    
    def test_empty_query_matches(self):
        """Test empty query matches everything"""
        entry = HostsEntry(ip="192.168.1.1", domain="example.com")
        assert entry.matches("")
        assert entry.matches(None) if hasattr(entry, 'matches') else True


class TestEntryDeletion:
    """Property-based tests for entry deletion
    
    Feature: hosts-viewer
    Property 2: Entry Deletion Correctness
    Validates: Requirements 3.3
    """
    
    @given(
        entries=st.lists(
            st.tuples(ip_strategy, domain_strategy),
            min_size=1, max_size=10,
            unique_by=lambda x: x[1]  # unique domains
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_entry_deletion_correctness(self, entries):
        """
        Property 2: Entry Deletion Correctness
        For any domain that exists in the hosts file, after deletion, 
        querying for that domain should return None, and the total 
        entry count should decrease by one.
        
        Feature: hosts-viewer
        Validates: Requirements 3.3
        """
        # Create temp hosts file with entries
        content = "\n".join([f"{ip} {domain}" for ip, domain in entries])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            manager = HostsManager(hosts_path=temp_path)
            
            # Get initial count
            initial_entries = manager.get_all_entries()
            initial_count = len(initial_entries)
            
            # Pick a random entry to delete
            import random
            entry_to_delete = random.choice(entries)
            domain_to_delete = entry_to_delete[1]
            
            # Verify entry exists before deletion
            assert manager.get_entry(domain_to_delete) is not None
            
            # Delete the entry
            success = manager.remove_entry(domain_to_delete)
            assert success, "Deletion should succeed"
            
            # Verify entry no longer exists
            assert manager.get_entry(domain_to_delete) is None, \
                f"Entry for {domain_to_delete} should be None after deletion"
            
            # Verify count decreased by 1
            final_entries = manager.get_all_entries()
            assert len(final_entries) == initial_count - 1, \
                f"Entry count should decrease by 1: {initial_count} -> {len(final_entries)}"
            
        finally:
            os.unlink(temp_path)
    
    def test_delete_nonexistent_entry(self):
        """Test deleting a non-existent entry returns True (no-op)"""
        content = "192.168.1.1 example.com\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            manager = HostsManager(hosts_path=temp_path)
            
            # Delete non-existent domain
            success = manager.remove_entry("nonexistent.com")
            assert success, "Deleting non-existent entry should return True"
            
            # Original entry should still exist
            assert manager.get_entry("example.com") is not None
        finally:
            os.unlink(temp_path)


class TestLocalhostFilter:
    """Tests for localhost/127.0.0.1 filtering functionality"""
    
    def test_localhost_ip_detected(self):
        """Test that 127.0.0.1 entries are detected as localhost"""
        entry = HostsEntry(ip="127.0.0.1", domain="localhost.sangfor.com.cn")
        assert is_localhost_entry(entry)
    
    def test_ipv6_localhost_detected(self):
        """Test that ::1 entries are detected as localhost"""
        entry = HostsEntry(ip="::1", domain="somehost")
        assert is_localhost_entry(entry)
    
    def test_localhost_domain_detected(self):
        """Test that domains containing 'localhost' are detected"""
        entry = HostsEntry(ip="192.168.1.1", domain="localhost.example.com")
        assert is_localhost_entry(entry)
    
    def test_normal_entry_not_localhost(self):
        """Test that normal entries are not detected as localhost"""
        entry = HostsEntry(ip="104.16.132.229", domain="betterclau.de")
        assert not is_localhost_entry(entry)
    
    def test_case_insensitive_localhost_detection(self):
        """Test that localhost detection is case-insensitive"""
        entry1 = HostsEntry(ip="192.168.1.1", domain="LOCALHOST.example.com")
        entry2 = HostsEntry(ip="192.168.1.1", domain="LocalHost.example.com")
        assert is_localhost_entry(entry1)
        assert is_localhost_entry(entry2)
    
    @given(
        ip=st.sampled_from(["127.0.0.1", "::1"]),
        domain=domain_strategy
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_localhost_ip_always_filtered(self, ip, domain):
        """
        Property: For any entry with localhost IP (127.0.0.1 or ::1),
        is_localhost_entry should return True.
        """
        entry = HostsEntry(ip=ip, domain=domain)
        assert is_localhost_entry(entry), f"Entry with IP {ip} should be detected as localhost"
    
    @given(
        ip=ip_strategy.filter(lambda x: x not in LOCALHOST_IPS),
        domain=domain_strategy.filter(lambda x: "localhost" not in x.lower())
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_non_localhost_not_filtered(self, ip, domain):
        """
        Property: For any entry without localhost IP and without 'localhost' in domain,
        is_localhost_entry should return False.
        """
        entry = HostsEntry(ip=ip, domain=domain)
        assert not is_localhost_entry(entry), f"Entry {ip} {domain} should not be detected as localhost"
