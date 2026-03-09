"""Unit tests for DocsRenderer."""

from pathlib import Path

from prism.tools.docs_server.renderer import render_file, render_markdown


class TestRenderMarkdown:
    def test_heading(self):
        result = render_markdown("# Hello World")
        assert "Hello World" in result
        assert "<h1>" in result or "<h1" in result

    def test_code_block(self):
        md = "```python\nprint('hello')\n```"
        result = render_markdown(md)
        assert "print" in result

    def test_bold_and_italic(self):
        result = render_markdown("**bold** and *italic*")
        assert "bold" in result
        assert "italic" in result

    def test_empty_string(self):
        result = render_markdown("")
        assert isinstance(result, str)

    def test_link(self):
        result = render_markdown("[link](https://example.com)")
        assert "example.com" in result


class TestRenderFile:
    def test_markdown_file(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nHello world.")
        result = render_file(md_file)
        assert "Test" in result
        assert "Hello world" in result

    def test_yaml_file(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("key: value\n")
        result = render_file(yaml_file)
        assert "key: value" in result
        assert "<pre>" in result

    def test_missing_file(self):
        result = render_file(Path("/nonexistent/file.md"))
        assert "Error" in result

    def test_plain_text(self, tmp_path):
        txt = tmp_path / "notes.txt"
        txt.write_text("Some notes here")
        result = render_file(txt)
        assert "Some notes" in result
