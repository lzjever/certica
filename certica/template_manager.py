"""
Template Manager - Handles template files for default values
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class TemplateManager:
    """Manages template files for default certificate values"""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir).resolve()
        self.templates_dir = self.base_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.default_template = "default.json"

    def create_template(
        self,
        template_name: str,
        organization: str = "Development",
        country: str = "CN",
        state: str = "Beijing",
        city: str = "Beijing",
        default_validity_days: int = 365,
        default_key_size: int = 2048,
    ) -> str:
        """Create a new template file"""
        template_path = self.templates_dir / f"{template_name}.json"

        template_data = {
            "organization": organization,
            "country": country,
            "state": state,
            "city": city,
            "default_validity_days": default_validity_days,
            "default_key_size": default_key_size,
        }

        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)

        return str(template_path)

    def load_template(self, template_name: Optional[str] = None) -> Dict:
        """Load a template file"""
        if template_name is None:
            template_name = self.default_template

        template_path = self.templates_dir / f"{template_name}.json"

        if not template_path.exists():
            # Return default values if template doesn't exist
            return {
                "organization": "Development",
                "country": "CN",
                "state": "Beijing",
                "city": "Beijing",
                "default_validity_days": 365,
                "default_key_size": 2048,
            }

        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_templates(self) -> List[str]:
        """List all available templates"""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            templates.append(template_file.stem)
        return templates

    def delete_template(self, template_name: str) -> bool:
        """Delete a template file"""
        template_path = self.templates_dir / f"{template_name}.json"
        if template_path.exists():
            template_path.unlink()
            return True
        return False
