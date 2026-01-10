"""
Property-based tests for URLParser and IPParser
Feature: cf-proxy-manager
Property 1: URL/Domain Parsing Round Trip
Property 2: IP Entry Parsing Consistency
Validates: Requirements 1.3, 2.2, 2.3, 3.3, 3.4
"""
from hypothesis import given, strategies as st, settings, HealthCheck

from cf_proxy_manager.models import IPEntry
from cf_proxy_manager.parsers import URLParser, IPParser


# Strategies
ip_octet = st.integers(min_value=0, max_value=255)
ip_strategy = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
    lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
)

port_strategy = st.integers(min_value=1, max_value=65535)

domain_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=3, max_size=10
).map(lambda s: f"{s}.com")

target_node_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789.-",
    min_size=3, max_size=20
).filter(lambda s: s and not s.startswith('.') and not s.endswith('.'))


class TestURLParserProperties:
    """Property-based tests for URLParser"""
    
    @given(cf_domain=domain_strategy, target_node=target_node_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_url_build_parse_round_trip(self, cf_domain: str, target_node: str):
        """
        Property 1: URL/Domain Parsing Round Trip
        For any valid CF domain and target node, building a URL and parsing it
        should recover the original domain and target.
        Validates: Requirements 2.2, 2.3
        """
        # Build URL
        full_url = URLParser.build_proxy_url(cf_domain, target_node)
        
        # Parse it back
        config = URLParser.parse_proxy_url(full_url)
        
        assert config is not None
        assert config.cf_domain == cf_domain
        assert config.target_node == target_node
    
    @given(domain=domain_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_domain_only_parsing(self, domain: str):
        """
        Test that domain-only input is correctly parsed.
        Validates: Requirements 2.3
        """
        config = URLParser.parse_proxy_url(domain)
        
        assert config is not None
        assert config.cf_domain == domain
    
    @given(url=st.text(min_size=1, max_size=50))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_extract_domain_consistency(self, url: str):
        """
        Test that extract_domain is consistent with parse_proxy_url.
        """
        config = URLParser.parse_proxy_url(url)
        extracted = URLParser.extract_domain(url)
        
        if config is not None:
            assert extracted == config.cf_domain or extracted == ""


class TestIPParserProperties:
    """Property-based tests for IPParser"""
    
    @given(ip=ip_strategy, port=port_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_ip_parse_format_round_trip(self, ip: str, port: int):
        """
        Property 2: IP Entry Parsing Consistency
        For any valid IP and port, parsing and formatting should be consistent.
        Validates: Requirements 3.3, 3.4
        """
        # Create entry string
        entry_str = f"{ip}:{port}"
        
        # Parse it
        ip_entry = IPParser.parse(entry_str)
        
        assert ip_entry is not None
        assert ip_entry.ip == ip
        assert ip_entry.port == port
        
        # Format it back
        formatted = IPParser.format(ip_entry)
        assert formatted == entry_str
    
    @given(ip=ip_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_ip_only_uses_default_port(self, ip: str):
        """
        Test that IP-only input uses default port 443.
        Validates: Requirements 3.4
        """
        ip_entry = IPParser.parse(ip)
        
        assert ip_entry is not None
        assert ip_entry.ip == ip
        assert ip_entry.port == 443
    
    @given(ip=ip_strategy, port=port_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_ip_with_location_tag(self, ip: str, port: int):
        """
        Test that location tags are ignored during parsing.
        Validates: Requirements 3.4
        """
        entry_str = f"{ip}:{port}#🇩🇪 法兰克福"
        
        ip_entry = IPParser.parse(entry_str)
        
        assert ip_entry is not None
        assert ip_entry.ip == ip
        assert ip_entry.port == port
    
    @given(ips=st.lists(
        st.tuples(ip_strategy, port_strategy),
        min_size=1, max_size=10
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_parse_multiple_preserves_all(self, ips):
        """
        Test that parse_multiple correctly parses all valid entries.
        """
        # Create multi-line input
        lines = [f"{ip}:{port}" for ip, port in ips]
        text = "\n".join(lines)
        
        # Parse
        entries = IPParser.parse_multiple(text)
        
        assert len(entries) == len(ips)
        for (orig_ip, orig_port), entry in zip(ips, entries):
            assert entry.ip == orig_ip
            assert entry.port == orig_port
    
    def test_invalid_ip_rejected(self):
        """Test that invalid IPs are rejected"""
        invalid_ips = [
            "256.1.1.1",
            "1.2.3",
            "1.2.3.4.5",
            "abc.def.ghi.jkl",
            "",
            "   ",
        ]
        
        for invalid in invalid_ips:
            result = IPParser.parse(invalid)
            assert result is None, f"Expected None for '{invalid}', got {result}"
