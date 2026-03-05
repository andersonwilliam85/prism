#!/usr/bin/env python3
"""
Hierarchical Config Merger

Merges configs from multiple levels: Company → Sub-Org → Dept → Team → User
Follows inheritance.yaml rules for deep merging, overrides, and conflict resolution.

Usage:
    from config_merger import load_merged_config
    
    config = load_merged_config(
        company="config/base/company.yaml",
        sub_org="config/orgs/engineering.yaml",
        department="config/departments/supply-chain.yaml",
        team="config/teams/receiving-systems.yaml",
        user="config/user-profile.yaml"
    )
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy
import os
import re


class ConfigMerger:
    """Handles hierarchical config merging with inheritance"""
    
    def __init__(self, inheritance_config_path="config/inheritance.yaml"):
        """Initialize with inheritance rules"""
        self.inheritance_path = Path(inheritance_config_path)
        
        if self.inheritance_path.exists():
            with open(self.inheritance_path) as f:
                self.rules = yaml.safe_load(f)
        else:
            # Default rules if inheritance.yaml not found
            self.rules = self._default_rules()
    
    def _default_rules(self) -> Dict:
        """Default merge rules if inheritance.yaml missing"""
        return {
            "merge_strategy": {
                "arrays": {
                    "tools_selected": "union",
                    "tools_excluded": "union",
                    "resources": "append",
                    "onboarding_tasks": "append"
                },
                "objects": {
                    "environment": "deep_merge",
                    "git": "override",
                    "career": "user_only",
                    "tools": "deep_merge"
                },
                "conflicts": {
                    "default": "override"
                }
            }
        }
    
    def load_merged_config(
        self,
        company: Optional[str] = None,
        sub_org: Optional[str] = None,
        department: Optional[str] = None,
        team: Optional[str] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load and merge configs from all levels
        
        Args:
            company: Path to company base config
            sub_org: Path to sub-organization config
            department: Path to department config
            team: Path to team config
            user: Path to user profile config
        
        Returns:
            Merged configuration dictionary
        """
        # Build chain of configs to merge
        chain = []
        
        if company:
            chain.append(("company", self._load_config(company)))
        if sub_org:
            chain.append(("sub_org", self._load_config(sub_org)))
        if department:
            chain.append(("department", self._load_config(department)))
        if team:
            chain.append(("team", self._load_config(team)))
        if user:
            chain.append(("user", self._load_config(user)))
        
        # Start with empty config
        merged = {}
        
        # Merge each level in order
        for level_name, config in chain:
            if config:
                merged = self._merge_level(merged, config, level_name)
        
        # Substitute environment variables
        merged = self._substitute_env_vars(merged)
        
        return merged
    
    def _load_config(self, path: str) -> Optional[Dict]:
        """Load a single config file"""
        config_path = Path(path)
        
        if not config_path.exists():
            return None
        
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def _merge_level(self, base: Dict, overlay: Dict, level: str) -> Dict:
        """Merge overlay config into base config"""
        result = deepcopy(base)
        
        for key, value in overlay.items():
            if key not in result:
                # New key, just add it
                result[key] = deepcopy(value)
            else:
                # Key exists, need to merge
                result[key] = self._merge_value(key, result[key], value, level)
        
        return result
    
    def _merge_value(self, key: str, base_value: Any, overlay_value: Any, level: str) -> Any:
        """
        Merge a single value based on merge strategy
        
        Args:
            key: Config key being merged
            base_value: Existing value
            overlay_value: New value to merge in
            level: Current config level (for context)
        """
        # Get merge strategy for this key
        strategy = self._get_merge_strategy(key)
        
        # Both are dicts - deep merge
        if isinstance(base_value, dict) and isinstance(overlay_value, dict):
            if strategy == "override":
                return deepcopy(overlay_value)
            elif strategy == "user_only" and level != "user":
                return deepcopy(base_value)  # Only user level can set this
            else:  # deep_merge
                return self._deep_merge_dicts(base_value, overlay_value)
        
        # Both are lists - merge based on array strategy
        elif isinstance(base_value, list) and isinstance(overlay_value, list):
            array_strategy = self._get_array_strategy(key)
            
            if array_strategy == "union":
                # Combine, remove duplicates
                return list(set(base_value + overlay_value))
            elif array_strategy == "append":
                # Keep all, in order
                return base_value + overlay_value
            else:  # override
                return deepcopy(overlay_value)
        
        # Different types or primitives - override
        else:
            return deepcopy(overlay_value)
    
    def _get_merge_strategy(self, key: str) -> str:
        """Get merge strategy for a specific key"""
        strategies = self.rules.get("merge_strategy", {}).get("objects", {})
        return strategies.get(key, self.rules.get("merge_strategy", {}).get("conflicts", {}).get("default", "override"))
    
    def _get_array_strategy(self, key: str) -> str:
        """Get array merge strategy for a specific key"""
        strategies = self.rules.get("merge_strategy", {}).get("arrays", {})
        return strategies.get(key, "override")
    
    def _deep_merge_dicts(self, base: Dict, overlay: Dict) -> Dict:
        """Recursively deep merge two dictionaries"""
        result = deepcopy(base)
        
        for key, value in overlay.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # Use append strategy for nested lists
                    result[key] = result[key] + value
                else:
                    result[key] = deepcopy(value)
            else:
                result[key] = deepcopy(value)
        
        return result
    
    def _substitute_env_vars(self, config: Dict) -> Dict:
        """
        Substitute ${VAR_NAME} placeholders with environment variables
        
        Supports:
        - ${VAR} - OS environment variable
        - ${VAR:-default} - With default value
        """
        def substitute_value(value: Any) -> Any:
            if isinstance(value, str):
                # Find all ${VAR} or ${VAR:-default} patterns
                pattern = r'\$\{([^}:]+)(?::-([^}]+))?\}'
                
                def replacer(match):
                    var_name = match.group(1)
                    default = match.group(2) or ""
                    return os.environ.get(var_name, default)
                
                return re.sub(pattern, replacer, value)
            
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            
            else:
                return value
        
        return substitute_value(config)


# Convenience function
def load_merged_config(
    company: Optional[str] = None,
    sub_org: Optional[str] = None,
    department: Optional[str] = None,
    team: Optional[str] = None,
    user: Optional[str] = None,
    inheritance_config: str = "config/inheritance.yaml"
) -> Dict[str, Any]:
    """
    Load and merge hierarchical configs
    
    Example:
        config = load_merged_config(
            company="config/base/company.yaml",
            sub_org="config/orgs/sub-organization.yaml",
            department="config/departments/engineering.yaml",
            team="config/teams/platform.yaml",
            user="config/user-profile.yaml"
        )
    """
    merger = ConfigMerger(inheritance_config)
    return merger.load_merged_config(
        company=company,
        sub_org=sub_org,
        department=department,
        team=team,
        user=user
    )


if __name__ == "__main__":
    # Test the merger
    import json
    
    config = load_merged_config(
        company="config/base/company.yaml",
        sub_org="config/orgs/engineering.yaml",
        department="config/departments/supply-chain.yaml",
        team="config/teams/receiving-systems.yaml"
    )
    
    print(json.dumps(config, indent=2))
