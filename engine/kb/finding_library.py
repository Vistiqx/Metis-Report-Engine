"""Finding knowledge base with JSON file storage for Metis Report Engine.

Provides reusable finding templates with CRUD operations and file-based persistence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# Default library path
DEFAULT_LIBRARY_PATH = Path(__file__).resolve().parents[2] / "data" / "findings_library.json"

# In-memory cache
_library_cache: Optional[Dict[str, Dict[str, Any]]] = None
_library_path: Optional[Path] = None


def _ensure_library_exists(path: Path) -> None:
    """Create default library if it doesn't exist."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        default_library = {
            "missing_mfa": {
                "title": "Missing Multi-Factor Authentication",
                "category": "Identity",
                "severity": "High",
                "summary": "Accounts are not protected by multi-factor authentication.",
            },
            "weak_password_policy": {
                "title": "Weak Password Policy",
                "category": "Authentication",
                "severity": "Medium",
                "summary": "Password policy does not enforce adequate complexity or rotation controls.",
            },
            "unencrypted_data_at_rest": {
                "title": "Unencrypted Data at Rest",
                "category": "Data Protection",
                "severity": "High",
                "summary": "Sensitive data is stored without encryption.",
            },
            "missing_access_controls": {
                "title": "Missing Access Controls",
                "category": "Authorization",
                "severity": "Critical",
                "summary": "Inadequate access controls allow unauthorized access to sensitive resources.",
            },
            "outdated_software": {
                "title": "Outdated Software Components",
                "category": "Vulnerability Management",
                "severity": "High",
                "summary": "Software components are outdated and may contain known vulnerabilities.",
            },
        }
        _save_library(default_library, path)


def _load_library(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Load finding library from JSON file.

    Args:
        path: Path to library file (uses default if None)

    Returns:
        Dictionary of finding templates
    """
    global _library_cache, _library_path

    target_path = path or DEFAULT_LIBRARY_PATH

    # Use cache if same path and cache exists
    if _library_cache is not None and _library_path == target_path:
        return _library_cache.copy()

    # Ensure library exists
    _ensure_library_exists(target_path)

    # Load from file
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            library = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        # Return empty library on error
        library = {}

    # Update cache
    _library_cache = library.copy()
    _library_path = target_path

    return library.copy()


def _save_library(library: Dict[str, Dict[str, Any]], path: Optional[Path] = None) -> None:
    """Save finding library to JSON file.

    Args:
        library: Dictionary of finding templates
        path: Path to library file (uses default if None)
    """
    global _library_cache, _library_path

    target_path = path or DEFAULT_LIBRARY_PATH

    # Ensure directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to file
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2, ensure_ascii=False)

    # Update cache
    _library_cache = library.copy()
    _library_path = target_path


def get_finding_template(key: str, library_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Get a finding template by key.

    Args:
        key: Template identifier
        library_path: Optional custom library path

    Returns:
        Finding template dictionary or None
    """
    library = _load_library(library_path)
    return library.get(key)


def list_finding_templates(library_path: Optional[Path] = None) -> List[str]:
    """List all available finding template keys.

    Args:
        library_path: Optional custom library path

    Returns:
        Sorted list of template keys
    """
    library = _load_library(library_path)
    return sorted(library.keys())


def search_finding_templates(
    query: str,
    category: Optional[str] = None,
    library_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Search finding templates by query string and optional category.

    Args:
        query: Search query (matches title, summary, category)
        category: Optional category filter
        library_path: Optional custom library path

    Returns:
        List of matching templates with their keys
    """
    library = _load_library(library_path)
    query_lower = query.lower()
    results = []

    for key, template in library.items():
        # Check category filter
        if category and template.get("category") != category:
            continue

        # Search in title and summary
        title = template.get("title", "").lower()
        summary = template.get("summary", "").lower()
        template_category = template.get("category", "").lower()

        if (query_lower in title or
            query_lower in summary or
            query_lower in template_category):
            results.append({
                "key": key,
                **template,
            })

    return results


def create_finding_template(
    key: str,
    template: Dict[str, Any],
    library_path: Optional[Path] = None,
    overwrite: bool = False,
) -> bool:
    """Create a new finding template.

    Args:
        key: Template identifier
        template: Template dictionary (must have title, severity, summary)
        library_path: Optional custom library path
        overwrite: Whether to overwrite existing template

    Returns:
        True if created successfully

    Raises:
        ValueError: If key exists and overwrite=False, or if template invalid
    """
    # Validate template
    required_fields = ["title", "severity", "summary"]
    for field in required_fields:
        if field not in template:
            raise ValueError(f"Template missing required field: {field}")

    library = _load_library(library_path)

    # Check if key exists
    if key in library and not overwrite:
        raise ValueError(f"Template key '{key}' already exists. Use overwrite=True to replace.")

    # Add template
    library[key] = template
    _save_library(library, library_path)

    return True


def update_finding_template(
    key: str,
    updates: Dict[str, Any],
    library_path: Optional[Path] = None,
) -> bool:
    """Update an existing finding template.

    Args:
        key: Template identifier
        updates: Dictionary of fields to update
        library_path: Optional custom library path

    Returns:
        True if updated successfully

    Raises:
        ValueError: If template doesn't exist
    """
    library = _load_library(library_path)

    if key not in library:
        raise ValueError(f"Template key '{key}' not found")

    # Update fields
    library[key].update(updates)
    _save_library(library, library_path)

    return True


def delete_finding_template(key: str, library_path: Optional[Path] = None) -> bool:
    """Delete a finding template.

    Args:
        key: Template identifier
        library_path: Optional custom library path

    Returns:
        True if deleted successfully

    Raises:
        ValueError: If template doesn't exist
    """
    library = _load_library(library_path)

    if key not in library:
        raise ValueError(f"Template key '{key}' not found")

    # Remove template
    del library[key]
    _save_library(library, library_path)

    return True


def get_templates_by_category(
    category: str,
    library_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Get all templates in a specific category.

    Args:
        category: Category name
        library_path: Optional custom library path

    Returns:
        List of templates with their keys
    """
    library = _load_library(library_path)
    results = []

    for key, template in library.items():
        if template.get("category") == category:
            results.append({
                "key": key,
                **template,
            })

    return results


def list_categories(library_path: Optional[Path] = None) -> List[str]:
    """List all unique categories in the library.

    Args:
        library_path: Optional custom library path

    Returns:
        Sorted list of category names
    """
    library = _load_library(library_path)
    categories = {template.get("category") for template in library.values() if template.get("category")}
    return sorted([c for c in categories if c is not None])


def reload_library(library_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Force reload library from disk (clear cache).

    Args:
        library_path: Optional custom library path

    Returns:
        Loaded library dictionary
    """
    global _library_cache, _library_path

    _library_cache = None
    _library_path = None

    return _load_library(library_path)


def apply_finding_template(
    finding: Dict[str, Any],
    template_key: str,
    library_path: Optional[Path] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Apply a finding template to a finding.

    Args:
        finding: Finding to update
        template_key: Template to apply
        library_path: Optional custom library path
        overwrite: Whether to overwrite existing fields

    Returns:
        Updated finding dictionary
    """
    template = get_finding_template(template_key, library_path)

    if template is None:
        raise ValueError(f"Template '{template_key}' not found")

    # Create copy of finding
    result = finding.copy()

    # Apply template fields
    template_fields = ["title", "category", "severity", "summary", "description"]
    for field in template_fields:
        if field in template:
            if overwrite or field not in result or not result[field]:
                result[field] = template[field]

    return result
