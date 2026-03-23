"""Tests for DL and FT training template file content.

These tests verify template FILE CONTENT (not execution -- templates need GPU/torch).
They check for correct placeholders, imports, and absence of Jinja2 syntax.
"""

from __future__ import annotations

import re
from pathlib import Path

# Templates are at repo_root/gsd-ml/templates/
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "gsd-ml" / "templates"


# ---------------------------------------------------------------------------
# DL Image Classification Template
# ---------------------------------------------------------------------------


class TestDLImageTemplate:
    """train-dl-image.py template content validation."""

    def test_dl_image_template_exists(self):
        assert (TEMPLATES_DIR / "train-dl-image.py").exists()

    def test_dl_image_template_placeholders(self):
        content = (TEMPLATES_DIR / "train-dl-image.py").read_text()
        for placeholder in [
            "__DATA_PATH__",
            "__IMG_SIZE__",
            "__BATCH_SIZE__",
            "__MODEL_NAME__",
            "__METRIC__",
            "__TIME_BUDGET_SEC__",
        ]:
            assert placeholder in content, f"Missing placeholder {placeholder}"

    def test_dl_image_template_imports(self):
        content = (TEMPLATES_DIR / "train-dl-image.py").read_text()
        assert "import timm" in content
        assert re.search(r"from prepare import.*load_image_data", content)

    def test_dl_image_template_no_jinja(self):
        content = (TEMPLATES_DIR / "train-dl-image.py").read_text()
        assert "{{" not in content, "Template contains Jinja2 {{ syntax"
        assert "{%" not in content, "Template contains Jinja2 {% syntax"

    def test_dl_image_template_mixed_precision(self):
        content = (TEMPLATES_DIR / "train-dl-image.py").read_text()
        assert "torch.amp.autocast" in content
        assert "GradScaler" in content


# ---------------------------------------------------------------------------
# DL Text Classification Template
# ---------------------------------------------------------------------------


class TestDLTextTemplate:
    """train-dl-text.py template content validation."""

    def test_dl_text_template_exists(self):
        assert (TEMPLATES_DIR / "train-dl-text.py").exists()

    def test_dl_text_template_placeholders(self):
        content = (TEMPLATES_DIR / "train-dl-text.py").read_text()
        for placeholder in [
            "__DATA_PATH__",
            "__MODEL_NAME__",
            "__BATCH_SIZE__",
            "__METRIC__",
            "__TIME_BUDGET_SEC__",
        ]:
            assert placeholder in content, f"Missing placeholder {placeholder}"

    def test_dl_text_template_imports(self):
        content = (TEMPLATES_DIR / "train-dl-text.py").read_text()
        assert "AutoModelForSequenceClassification" in content
        assert re.search(r"from prepare import.*load_text_data", content)

    def test_dl_text_template_no_jinja(self):
        content = (TEMPLATES_DIR / "train-dl-text.py").read_text()
        assert "{{" not in content, "Template contains Jinja2 {{ syntax"
        assert "{%" not in content, "Template contains Jinja2 {% syntax"


# ---------------------------------------------------------------------------
# FT Template
# ---------------------------------------------------------------------------


class TestFTTemplate:
    """train-ft.py template content validation."""

    def test_ft_template_exists(self):
        assert (TEMPLATES_DIR / "train-ft.py").exists()

    def test_ft_template_placeholders(self):
        content = (TEMPLATES_DIR / "train-ft.py").read_text()
        for placeholder in [
            "__MODEL_NAME__",
            "__LORA_R__",
            "__LORA_ALPHA__",
            "__METRIC__",
            "__MAX_LENGTH__",
            "__BATCH_SIZE__",
            "__LEARNING_RATE__",
            "__NUM_EPOCHS__",
            "__DATA_PATH__",
        ]:
            assert placeholder in content, f"Missing placeholder {placeholder}"

    def test_ft_template_qlora(self):
        content = (TEMPLATES_DIR / "train-ft.py").read_text()
        assert "BitsAndBytesConfig" in content
        assert "get_peft_model" in content

    def test_ft_template_sfttrainer(self):
        content = (TEMPLATES_DIR / "train-ft.py").read_text()
        assert "SFTTrainer" in content
        assert "processing_class" in content

    def test_ft_template_no_jinja(self):
        content = (TEMPLATES_DIR / "train-ft.py").read_text()
        assert "{{" not in content, "Template contains Jinja2 {{ syntax"
        assert "{%" not in content, "Template contains Jinja2 {% syntax"

    def test_ft_metrics_functions(self):
        content = (TEMPLATES_DIR / "train-ft.py").read_text()
        assert "evaluate_perplexity" in content
        assert "evaluate_rouge" in content
