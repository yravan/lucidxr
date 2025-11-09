import os
import sys

import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vuer_mujoco.scripts.util.case_converter import pascal_to_snake, snake_to_pascal


class TestCaseConverter:
    def assert_pascal_to_snake(self, pascal, expected_snake):
        """Helper to assert pascal-to-snake conversion"""
        assert pascal_to_snake(pascal) == expected_snake, f"Failed to convert {pascal} to {expected_snake}"

    def assert_snake_to_pascal(self, snake, expected_pascal):
        """Helper to assert snake-to-pascal conversion"""
        assert snake_to_pascal(snake) == expected_pascal, f"Failed to convert {snake} to {expected_pascal}"

    def assert_roundtrip(self, original_pascal):
        """Helper to assert roundtrip conversion"""
        snake = pascal_to_snake(original_pascal)
        back_to_pascal = snake_to_pascal(snake)
        # Note: The roundtrip might not be exact due to capitalization of acronyms
        # For example, HTMLParser -> html_parser -> HtmlParser
        assert back_to_pascal.lower() == original_pascal.lower(), f"Failed roundtrip for {original_pascal}"

    def test_acronyms_to_snake(self):
        """Test converting acronyms from PascalCase to snake_case"""
        self.assert_pascal_to_snake("EnvSGD", "env_sgd")
        self.assert_pascal_to_snake("HTMLParser", "html_parser")
        self.assert_pascal_to_snake("XMLHttpRequest", "xml_http_request")
        self.assert_pascal_to_snake("UserID", "user_id")
        self.assert_pascal_to_snake("GPTModel", "gpt_model")

    def test_simple_pascal_to_snake(self):
        """Test converting simple PascalCase to snake_case"""
        self.assert_pascal_to_snake("SimpleTest", "simple_test")
        self.assert_pascal_to_snake("A", "a")

    def test_edge_cases_pascal_to_snake(self):
        """Test edge cases for PascalCase to snake_case"""
        self.assert_pascal_to_snake("", "")

    def test_acronyms_to_pascal(self):
        """Test converting acronyms from snake_case to PascalCase"""
        self.assert_snake_to_pascal("env_sgd", "EnvSgd")
        self.assert_snake_to_pascal("html_parser", "HtmlParser")
        self.assert_snake_to_pascal("xml_http_request", "XmlHttpRequest")
        self.assert_snake_to_pascal("user_id", "UserId")
        self.assert_snake_to_pascal("gpt_model", "GptModel")

    def test_simple_snake_to_pascal(self):
        """Test converting simple snake_case to PascalCase"""
        self.assert_snake_to_pascal("simple_test", "SimpleTest")
        self.assert_snake_to_pascal("a", "A")

    def test_edge_cases_snake_to_pascal(self):
        """Test edge cases for snake_case to PascalCase"""
        self.assert_snake_to_pascal("", "")

    def test_html_roundtrip(self):
        """Test HTML-related roundtrip conversions"""
        self.assert_roundtrip("HTMLParser")
        self.assert_roundtrip("XMLHttpRequest")

    def test_id_roundtrip(self):
        """Test ID-related roundtrip conversions"""
        self.assert_roundtrip("UserID")

    def test_simple_roundtrip(self):
        """Test simple roundtrip conversions"""
        self.assert_roundtrip("SimpleClass")


if __name__ == "__main__":
    pytest.main()
