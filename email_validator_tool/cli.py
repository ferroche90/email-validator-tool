import asyncio
from pathlib import Path
import typer
from loguru import logger

from email_validator_tool.config import update_settings
from email_validator_tool.core.loader import EmailLoader
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import generate_summary

app = typer.Typer(
    name="email-validator",
    help="Email validator with multiple verification layers",
    add_completion=False
)

@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="Path to CSV file with emails to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_path: Path = typer.Argument(
        ...,
        help="Path to save the CSV with results",
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
    enable_catch_all: bool = typer.Option(
        False,
        "--enable-catch-all",
        help="Enable catch-all detection (phase 2)",
    ),
    enable_smtp: bool = typer.Option(
        False,
        "--enable-smtp",
        help="Enable SMTP verification (phase 3)",
    ),
):
    """
    Validate a list of email addresses applying multiple verification layers.
    Results are saved to a CSV file and a statistical summary is displayed.
    """
    try:
        # Update global configuration based on CLI options
        settings = update_settings(
            enable_catch_all=enable_catch_all if enable_catch_all else None,
            enable_smtp=enable_smtp if enable_smtp else None
        )
        
        logger.info(f"Configuration: ENABLE_CATCH_ALL={settings.ENABLE_CATCH_ALL}, ENABLE_SMTP={settings.ENABLE_SMTP}")
        
        # Load emails
        logger.info(f"Loading emails from {input_path}")
        emails = EmailLoader.load_emails_from_csv(str(input_path))
        
        # Process emails and write results incrementally
        logger.info(f"Processing {len(emails)} emails...")
        processed_results = []
        
        async def process_and_write():
            pipeline = ValidationPipeline()
            async for result in pipeline.run_pipeline(emails):
                processed_results.append(result)
                # Write results incrementally
                EmailLoader.write_results_to_csv(processed_results, str(output_path))
        
        # Run the pipeline
        asyncio.run(process_and_write())
        
        # Generate summary
        generate_summary(processed_results)
        
        logger.success(f"Process completed. Results saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
