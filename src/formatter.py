import logging
from pathlib import Path 
from src.ai_processor import FinalReport 

logger = logging.getLogger(__name__)

def to_markdown(report : FinalReport) -> str :
    """
    Converts the structutred FinalReport object into a clean Markdown string
    """
    md_lines = []

    md_lines.append("# AI Ops Document Report")
    md_lines.append("\n## Executive Summary\n")
    md_lines.append(report.executive_summary)


    md_lines.append("\n## Action Items")
    if report.consolidated_action_items:
        md_lines.append("| Priority | Description | Owner |")
        md_lines.append("| :--- | :--- | :--- |")

        priority_map = {"High" : 0 , "Medium" : 1 , "Low" : 2 }
        sorted_items = sorted(
            report.consolidated_action_items, 
            key=lambda x: priority_map.get(x.priority, 3)
        )

        for item in sorted_items:
            owner = item.owner or "Unassigned"
            desc = item.description.replace("|", "-")
            md_lines.append(f"| {item.priority} | {desc} | {owner} |")
    else:
        md_lines.append(" No immediate action items detected. ")

    return "\n".join(md_lines)

def save_report(report: FinalReport, input_path: Path) -> Path:
    """
    Saves the report to a Markdown file next to the original input file.
    Returns the path to the new report.
    """

    output_path = input_path.with_name(f"{input_path.stem}_report.md")

    markdown_content = to_markdown(report)

    try:
        output_path.write_text(markdown_content, encoding = "utf-8")
        logger.info(f"Report saved successfully to : {output_path}")
        return output_path
    except IOError as e:
        logger.error(f"Failed to save report to {output_path} : {e}")
        raise