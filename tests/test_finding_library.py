"""Tests for finding library module."""

import pytest
import json
import tempfile
from pathlib import Path
from engine.kb.finding_library import (
    get_finding_template,
    list_finding_templates,
    search_finding_templates,
    create_finding_template,
    update_finding_template,
    delete_finding_template,
    get_templates_by_category,
    list_categories,
    apply_finding_template,
    reload_library,
    _load_library,
)


class TestGetFindingTemplate:
    """Test retrieving finding templates."""
    
    def test_get_existing_template(self, tmp_path):
        # Create a temp library file
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "test_finding": {
                "title": "Test Finding",
                "category": "Test",
                "severity": "High",
                "summary": "Test summary",
            }
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        result = get_finding_template("test_finding", lib_file)
        
        assert result is not None
        assert result["title"] == "Test Finding"
        assert result["severity"] == "High"
    
    def test_get_missing_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        result = get_finding_template("nonexistent", lib_file)
        
        assert result is None
    
    def test_get_template_creates_default(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        # Library doesn't exist yet
        
        result = get_finding_template("missing_mfa", lib_file)
        
        # Should create default library
        assert result is not None
        assert "title" in result


class TestListFindingTemplates:
    """Test listing finding templates."""
    
    def test_list_returns_sorted_keys(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "z_finding": {"title": "Z", "severity": "High", "summary": "Z"},
            "a_finding": {"title": "A", "severity": "Medium", "summary": "A"},
            "m_finding": {"title": "M", "severity": "Low", "summary": "M"},
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        result = list_finding_templates(lib_file)
        
        assert result == ["a_finding", "m_finding", "z_finding"]
    
    def test_list_empty_library(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        result = list_finding_templates(lib_file)
        
        assert result == []


class TestSearchFindingTemplates:
    """Test searching finding templates."""
    
    def test_search_by_title(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "auth_finding": {
                "title": "Authentication Issue",
                "category": "Security",
                "severity": "High",
                "summary": "Auth problem",
            },
            "network_finding": {
                "title": "Network Issue",
                "category": "Infrastructure",
                "severity": "Medium",
                "summary": "Network problem",
            },
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        results = search_finding_templates("auth", library_path=lib_file)
        
        assert len(results) == 1
        assert results[0]["key"] == "auth_finding"
    
    def test_search_by_category(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "f1": {"title": "F1", "category": "Security", "severity": "High", "summary": "S1"},
            "f2": {"title": "F2", "category": "Security", "severity": "Medium", "summary": "S2"},
            "f3": {"title": "F3", "category": "Other", "severity": "Low", "summary": "S3"},
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        results = search_finding_templates("f", category="Security", library_path=lib_file)
        
        assert len(results) == 2
        keys = [r["key"] for r in results]
        assert "f1" in keys
        assert "f2" in keys
        assert "f3" not in keys


class TestCreateFindingTemplate:
    """Test creating finding templates."""
    
    def test_create_new_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        template = {
            "title": "New Finding",
            "category": "Test",
            "severity": "High",
            "summary": "Test finding summary",
        }
        
        result = create_finding_template("new_key", template, lib_file)
        
        assert result is True
        
        # Verify it was saved
        saved = get_finding_template("new_key", lib_file)
        assert saved["title"] == "New Finding"
    
    def test_create_duplicate_without_overwrite(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {"existing": {"title": "Existing", "severity": "High", "summary": "S"}}
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        with pytest.raises(ValueError, match="already exists"):
            create_finding_template("existing", {"title": "New", "severity": "Low", "summary": "N"}, lib_file)
    
    def test_create_duplicate_with_overwrite(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {"existing": {"title": "Old", "severity": "High", "summary": "Old"}}
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        template = {"title": "New", "severity": "Low", "summary": "New"}
        result = create_finding_template("existing", template, lib_file, overwrite=True)
        
        assert result is True
        saved = get_finding_template("existing", lib_file)
        assert saved["title"] == "New"
    
    def test_create_missing_required_fields(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        
        with pytest.raises(ValueError, match="missing required field"):
            create_finding_template("bad", {"title": "No Severity"}, lib_file)


class TestUpdateFindingTemplate:
    """Test updating finding templates."""
    
    def test_update_existing_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {"existing": {"title": "Old", "severity": "High", "summary": "Old", "category": "Test"}}
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        result = update_finding_template("existing", {"title": "Updated"}, lib_file)
        
        assert result is True
        saved = get_finding_template("existing", lib_file)
        assert saved["title"] == "Updated"
        assert saved["severity"] == "High"  # Unchanged
    
    def test_update_nonexistent_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        with pytest.raises(ValueError, match="not found"):
            update_finding_template("missing", {"title": "New"}, lib_file)


class TestDeleteFindingTemplate:
    """Test deleting finding templates."""
    
    def test_delete_existing_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {"todelete": {"title": "To Delete", "severity": "High", "summary": "D"}}
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        result = delete_finding_template("todelete", lib_file)
        
        assert result is True
        assert get_finding_template("todelete", lib_file) is None
    
    def test_delete_nonexistent_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        with pytest.raises(ValueError, match="not found"):
            delete_finding_template("missing", lib_file)


class TestGetTemplatesByCategory:
    """Test getting templates by category."""
    
    def test_get_by_category(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "f1": {"title": "F1", "category": "Security", "severity": "High", "summary": "S1"},
            "f2": {"title": "F2", "category": "Security", "severity": "Medium", "summary": "S2"},
            "f3": {"title": "F3", "category": "Other", "severity": "Low", "summary": "S3"},
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        results = get_templates_by_category("Security", lib_file)
        
        assert len(results) == 2
        keys = [r["key"] for r in results]
        assert "f1" in keys
        assert "f2" in keys


class TestListCategories:
    """Test listing categories."""
    
    def test_list_unique_categories(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "f1": {"title": "F1", "category": "Security", "severity": "High", "summary": "S1"},
            "f2": {"title": "F2", "category": "Security", "severity": "Medium", "summary": "S2"},
            "f3": {"title": "F3", "category": "Infrastructure", "severity": "Low", "summary": "S3"},
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        results = list_categories(lib_file)
        
        assert sorted(results) == ["Infrastructure", "Security"]


class TestApplyFindingTemplate:
    """Test applying templates to findings."""
    
    def test_apply_template_to_finding(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "template1": {
                "title": "Template Title",
                "category": "Security",
                "severity": "Critical",
                "summary": "Template summary",
            }
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        finding = {"id": "F-001"}  # Missing most fields
        result = apply_finding_template(finding, "template1", lib_file)
        
        assert result["title"] == "Template Title"
        assert result["category"] == "Security"
        assert result["severity"] == "Critical"
        assert result["id"] == "F-001"  # Original preserved
    
    def test_apply_template_with_overwrite(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "template1": {
                "title": "Template Title",
                "category": "Security",
                "severity": "Critical",
                "summary": "Template summary",
            }
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        finding = {"id": "F-001", "title": "Original Title", "severity": "Low"}
        result = apply_finding_template(finding, "template1", lib_file, overwrite=True)
        
        assert result["title"] == "Template Title"  # Overwritten
        assert result["severity"] == "Critical"  # Overwritten
    
    def test_apply_template_without_overwrite(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        test_lib = {
            "template1": {
                "title": "Template Title",
                "severity": "Critical",
                "summary": "Template summary",
            }
        }
        with open(lib_file, "w") as f:
            json.dump(test_lib, f)
        
        finding = {"id": "F-001", "title": "Original Title"}
        result = apply_finding_template(finding, "template1", lib_file, overwrite=False)
        
        assert result["title"] == "Original Title"  # Preserved
        assert result["severity"] == "Critical"  # Filled in
    
    def test_apply_missing_template(self, tmp_path):
        lib_file = tmp_path / "test_library.json"
        lib_file.write_text("{}")
        
        with pytest.raises(ValueError, match="not found"):
            apply_finding_template({}, "missing", lib_file)
