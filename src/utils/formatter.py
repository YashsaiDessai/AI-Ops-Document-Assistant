import json
from pathlib import Path
from src.models.extraction import FinalReport
from src.core.logging import get_logger

logger = get_logger(__name__)


def to_markdown(report: FinalReport) -> str:
    """
    Converts a structured FinalReport object into a formatted Markdown string.
    """
    md_lines = []

    md_lines.append("# AI Ops Document Report")
    md_lines.append("\n## Executive Summary\n")
    md_lines.append(report.executive_summary)

    md_lines.append("\n## Action Items")
    if report.consolidated_action_items:
        md_lines.append("\n| Priority | Description | Owner |")
        md_lines.append("| :--- | :--- | :--- |")

        # Prioritize sorting (High -> Medium -> Low)
        priority_map = {"High": 0, "Medium": 1, "Low": 2}
        sorted_items = sorted(
            report.consolidated_action_items,
            key=lambda x: priority_map.get(x.priority.capitalize(), 3)
        )

        for item in sorted_items:
            owner = item.owner or "Unassigned"
            desc = item.description.replace("|", "-")
            md_lines.append(f"| {item.priority.capitalize()} | {desc} | {owner} |")
    else:
        md_lines.append("\nNo immediate action items detected.")

    return "\n".join(md_lines)


def to_json(report: FinalReport) -> str:
    """
    Converts a structured FinalReport object into a raw JSON string.
    """
    return report.model_dump_json(indent=2)


def save_report(content: str, output_path: Path) -> Path:
    """
    Writes the serialized report content to the designated output path.
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info("Report file saved successfully", file_path=str(output_path))
        return output_path
    except IOError as e:
        logger.error("Failed to write report file to disk", file_path=str(output_path), error=str(e))
        raise
