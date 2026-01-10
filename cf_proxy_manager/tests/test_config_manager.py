"""
Property-based tests for ConfigManager
Feature: cf-proxy-manager, Property 7: Configuration Round Trip
Validates: Requirements 6.1, 6.3
"""
import os
import tempfile
from hypothesis import given, strategies as st, settings, HealthCheck

from cf_proxy_manager.models import Config, IPEntry
from cf_proxy_manager.config_manager import ConfigManager


# Strategies for generating test data - simplified for speed
ip_octet = st.integers(min_value=0, max_value=255)
ip_strategy = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
    lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
)

ip_entry_strategy = st.builds(
    IPEntry,
    ip=ip_strategy,
    port=st.integers(min_value=1, max_value=65535)
)

domain_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=3, max_size=10
).map(lambda s: f"{s}.com")

config_strategy = st.builds(
    Config,
    target_nodes=st.lists(domain_strategy, min_size=0, max_size=5),
    current_target_node=domain_strategy,
    cf_proxy_domain=domain_strategy | st.just(""),
    ip_list=st.lists(ip_entry_strategy, min_size=0, max_size=10),
    selected_ip=ip_strategy | st.none()
)


class TestConfigManagerProperties:
    """Property-based tests for ConfigManager"""
    
    @given(config=config_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_config_round_trip(self, config: Config):
        """
        Property 7: Configuration Round Trip
        For any valid Config object, serializing to JSON and deserializing 
        should produce an equivalent Config object.
        Validates: Requirements 6.1, 6.3
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            # Save config
            assert manager.save(config) is True
            
            # Load config back
            loaded_config = manager.load()
            
            # Verify all fields are preserved
            assert loaded_config.target_nodes == config.target_nodes
            assert loaded_config.current_target_node == config.current_target_node
            assert loaded_config.cf_proxy_domain == config.cf_proxy_domain
            assert loaded_config.selected_ip == config.selected_ip
            
            # Verify IP list
            assert len(loaded_config.ip_list) == len(config.ip_list)
            for orig, loaded in zip(config.ip_list, loaded_config.ip_list):
                assert orig.ip == loaded.ip
                assert orig.port == loaded.port
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_default_config_has_required_fields(self):
        """Test that default config contains all required fields"""
        manager = ConfigManager("nonexistent.json")
        config = manager.get_default_config()
        
        assert len(config.target_nodes) > 0
        assert config.current_target_node != ""
        assert len(config.ip_list) > 0
