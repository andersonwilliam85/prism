"""Tests for prism.utilities.env_substitutor."""

import os
from unittest.mock import patch

from prism.utilities.env_substitutor import substitute


class TestSubstitute:
    def test_simple_var(self):
        with patch.dict(os.environ, {"MY_VAR": "hello"}):
            assert substitute("${MY_VAR}") == "hello"

    def test_var_with_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert substitute("${MISSING:-fallback}") == "fallback"

    def test_var_present_ignores_default(self):
        with patch.dict(os.environ, {"MY_VAR": "real"}):
            assert substitute("${MY_VAR:-fallback}") == "real"

    def test_missing_var_no_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert substitute("${NOPE}") == ""

    def test_embedded_in_string(self):
        with patch.dict(os.environ, {"HOST": "localhost", "PORT": "8080"}):
            assert substitute("http://${HOST}:${PORT}") == "http://localhost:8080"

    def test_dict_recursive(self):
        with patch.dict(os.environ, {"DB": "postgres"}):
            result = substitute({"url": "jdbc:${DB}", "nested": {"x": "${DB}"}})
            assert result == {"url": "jdbc:postgres", "nested": {"x": "postgres"}}

    def test_list_recursive(self):
        with patch.dict(os.environ, {"A": "1"}):
            assert substitute(["${A}", "literal"]) == ["1", "literal"]

    def test_non_string_passthrough(self):
        assert substitute(42) == 42
        assert substitute(True) is True
        assert substitute(None) is None
