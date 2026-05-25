import argparse
import sys
import asyncio
from pathlib import Path
from src.core.logging import configure_logging, get_logger
from src.core.exceptions import AppError
from src.pipelines.document import DocumentPipeline

logger = get_logger("Orchestrator")


def parse_arguments() -> argparse.Namespace:
    """
    Defines and parses command-line interface arguments.
    """
    parser = argparse.ArgumentParser(
        description="AI Ops Document Assistant - Synthesize document logs/reports into actionable insights."
    )
    parser.add_argument(
        "filepath",
        type=Path,
        help="Path to the input document (supports .pdf and .txt)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="Directory to save the generated report artifacts (defaults to the directory of the input file)"
    )
    parser.add_argument(
        "-c", "--chunk-size",
        type=int,
        default=None,
        help="Character size threshold for document splitting (overrides config setting)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable detailed debug-level logging output"
    )
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for command-line execution.
    """
    args = parse_arguments()

    # Configure global logging systems
    configure_logging(verbose=args.verbose)

    logger.info("Starting AI Ops Document Assistant CLI orchestration")

    if not args.filepath.exists():
        logger.error("Target document file not found on disk", target_path=str(args.filepath))
        sys.exit(1)

    try:
        pipeline = DocumentPipeline()
        # Initialize and run the async pipeline
        asyncio.run(pipeline.run(
            filepath=args.filepath,
            output_dir=args.output_dir,
            chunk_size=args.chunk_size
        ))
    except AppError as e:
        logger.error("Execution pipeline encountered a managed error", error=str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("An unhandled critical error forced execution abort.")
        sys.exit(1)


if __name__ == "__main__":
    main()
