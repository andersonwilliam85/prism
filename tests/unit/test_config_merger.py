"""
Unit tests for configuration merger.
"""
import pytest
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from config_merger import ConfigMerger, merge_configs


@pytest.mark.unit
class TestConfigMerger:
    """Test configuration merging logic."""
    
    def test_merges_simple_configs(self):
        """Test merging of simple flat configs."""
        base = {"name": "Base", "version": "1.0"}
        override = {"version": "2.0", "author": "Test"}
        
        result = merge_configs(base, override)
        
        assert result["name"] == "Base"
        assert result["version"] == "2.0"  # Override
        assert result["author"] == "Test"
    
    def test_merges_nested_configs(self):
        """Test merging of nested configurations."""
        base = {
            "package": {
                "name": "test",
                "settings": {
                    "debug": False
                }
            }
        }
        
        override = {
            "package": {
                "settings": {
                    "debug": True,
                    "verbose": True
                }
            }
        }
        
        result = merge_configs(base, override)
        
        assert result["package"]["name"] == "test"
        assert result["package"]["settings"]["debug"] is True
        assert result["package"]["settings"]["verbose"] is True
    
    def test_merges_lists(self):
        """Test merging of list values."""
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}
        
        result = merge_configs(base, override)
        
        # Lists should be extended
        assert 1 in result["items"]
        assert 4 in result["items"]
    
    def test_preserves_base_when_override_missing(self):
        """Test that base values are preserved when not overridden."""
        base = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        override = {"field2": "new_value2"}
        
        result = merge_configs(base, override)
        
        assert result["field1"] == "value1"
        assert result["field2"] == "new_value2"
        assert result["field3"] == "value3"
    
    def test_handles_null_values(self):
        """Test handling of null/None values."""
        base = {"field": "value"}
        override = {"field": None}
        
        result = merge_configs(base, override)
        
        # None should override
        assert result["field"] is None
    
    def test_deep_merge(self):
        """Test deep merging of nested structures."""
        base = {
            "level1": {
                "level2": {
                    "level3": {
                        "field": "base"
                    }
                }
            }
        }
        
        override = {
            "level1": {
                "level2": {
                    "level3": {
                        "field": "override",
                        "new_field": "new"
                    }
                }
            }
        }
        
        result = merge_configs(base, override)
        
        assert result["level1"]["level2"]["level3"]["field"] == "override"
        assert result["level1"]["level2"]["level3"]["new_field"] == "new"


@pytest.mark.unit
class TestConfigMergerClass:
    """Test ConfigMerger class functionality."""
    
    def test_initializes(self):
        """Test that ConfigMerger initializes."""
        merger = ConfigMerger()
        assert merger is not None
    
    def test_merges_multiple_configs(self):
        """Test merging multiple configuration layers."""
        merger = ConfigMerger()
        
        base = {"a": 1, "b": 2}
        org = {"b": 20, "c": 3}
        team = {"c": 30, "d": 4}
        
        result = merger.merge([base, org, team])
        
        assert result["a"] == 1
        assert result["b"] == 20
        assert result["c"] == 30
        assert result["d"] == 4
