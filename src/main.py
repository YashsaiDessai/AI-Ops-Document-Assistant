import argparse
import sys
import logging
from pathlib import Path
from typing import List
from src import config, loader, chunker, ai_processor, formatter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Orchestrator")

def parse_arguments() -> argparse.Namespace:
    """
    Defines CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Extract summaries and action items."
    )
    parser.add_argument(
        "filepath",
        type=Path,
        help="Path to the input Doc"
    )
    parser.add_argument(
        "--verbose",
        action = "store_true",
        help = "Enable debug logging"
    )
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    if args.verbose:
        logger.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    if not args.filepath.exists():
        logger.error(f"File not found : {args.filepath}")
        sys.exit(1)

    logger.info(f"Starting pipeline for: {args.filepath.name}")
    
    try:
        # 2. Configuration Validation (Fail Fast)
        # This will raise an error immediately if the API key is missing.
        cfg = config.load_config()
        logger.debug(f"Configuration loaded. Target Model: {cfg.model_name}")

        # 3. Document Ingestion
        logger.info("Phase 1: Ingesting document...")
        raw_text = loader.load_document(args.filepath)
        logger.info(f"Successfully loaded {len(raw_text)} characters.")

        # 4. Smart Chunking
        logger.info("Phase 2: Chunking text...")
        chunks = chunker.recursive_split(
            raw_text, 
            max_chunk_size=cfg.chunk_size
        )
        if not chunks:
            logger.error("Document appears empty after processing.")
            sys.exit(1)
        logger.info(f"Document split into {len(chunks)} chunks.")

        # 5. Map Phase (Analysis)
        # We loop through chunks and process them. In a larger system,
        # this would be parallelized (asyncio), but for a CLI, a loop is safer/simpler.
        logger.info("Phase 3: Analyzing chunks with AI (Map Phase)...")
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            # Process chunk and append result
            analysis = ai_processor.analyze_chunk(chunk, i)
            chunk_analyses.append(analysis)
            print(f".", end="", flush=True) # Simple progress bar
        print() # Newline after progress dots

        # 6. Reduce Phase (Synthesis)
        logger.info("Phase 4: Synthesizing final report (Reduce Phase)...")
        final_report = ai_processor.synthesize_report(chunk_analyses)

        # 7. Reporting & Artifact Generation
        logger.info("Phase 5: Saving output...")
        
        # Print to Console
        print("\n" + "="*40)
        print(formatter.to_markdown(final_report))
        print("="*40 + "\n")

        # Save to File
        output_path = formatter.save_report(final_report, args.filepath)
        logger.info(f"✅ Report generated successfully: {output_path}")

    except Exception as e:
      # Catch-all for unexpected crashes (API errors, file permission issues)
      logger.exception("CRITICAL FAILURE: The pipeline stopped unexpectedly.")
      sys.exit(1)

if __name__ == "__main__":
    main()

    