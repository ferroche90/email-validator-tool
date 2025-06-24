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
    add_completion=False,
)


@app.callback()
def callback():
    """Email validator with multiple verification layers"""
    pass


@app.command()
def validate(
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
            enable_smtp=enable_smtp if enable_smtp else None,
        )

        logger.info(
            f"Configuration: ENABLE_CATCH_ALL={settings.ENABLE_CATCH_ALL}, ENABLE_SMTP={settings.ENABLE_SMTP}"
        )

        # Load emails
        logger.info(f"Loading emails from {input_path}")
        emails = EmailLoader.load_emails_from_csv(str(input_path))

        # Initialize CSV file with header
        logger.info(f"Initializing CSV file: {output_path}")
        EmailLoader.write_csv_header(str(output_path))

        # Process emails and write results incrementally
        logger.info(f"Processing {len(emails)} emails...")
        processed_results = []

        async def process_and_write():
            pipeline = ValidationPipeline(
                enable_smtp=settings.ENABLE_SMTP,
                enable_catch_all=settings.ENABLE_CATCH_ALL,
            )
            processed_count = 0
            async for result in pipeline.run_pipeline(emails):
                processed_results.append(result)
                # Append result to CSV file efficiently
                EmailLoader.append_result_to_csv(result, str(output_path))
                processed_count += 1
                # Log progress every 100 emails or for the last email
                if processed_count % 100 == 0 or processed_count == len(emails):
                    logger.info(
                        f"Progress: {processed_count}/{len(emails)} emails processed and saved to CSV"
                    )

        # Run the pipeline
        asyncio.run(process_and_write())

        # Generate summary
        generate_summary(processed_results)

        logger.success(f"Process completed. Results saved to {output_path}")

    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise typer.Exit(1)


@app.command()
def clear_cache():
    """Clear the DNS cache"""
    try:
        pipeline = ValidationPipeline()
        removed_count = pipeline.clear_dns_cache()
        logger.success(
            f"DNS cache cleared successfully. Removed {removed_count} entries."
        )
    except Exception as e:
        logger.error(f"Error clearing DNS cache: {str(e)}")
        raise typer.Exit(1)


@app.command()
def cache_stats():
    """Show DNS cache statistics"""
    try:
        pipeline = ValidationPipeline()
        stats = pipeline.get_dns_cache_stats()

        logger.info("DNS Cache Statistics:")
        logger.info(f"  Total entries: {stats['total_entries']}")
        logger.info(f"  Valid entries: {stats['valid_entries']}")
        logger.info(f"  Expired entries: {stats['expired_entries']}")
        logger.info(f"  Cache TTL: {stats['cache_ttl_seconds']} seconds")

    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}")
        raise typer.Exit(1)


@app.command()
def cleanup_cache():
    """Clean up expired DNS cache entries"""
    try:
        pipeline = ValidationPipeline()
        removed_count = pipeline.cleanup_expired_dns_cache()
        logger.success(
            f"Expired cache entries cleaned up. Removed {removed_count} entries."
        )
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}")
        raise typer.Exit(1)


@app.command()
def reload_bounce_list():
    """Reload the bounce list from the database"""
    try:
        pipeline = ValidationPipeline()
        bounce_count = pipeline.reload_bounce_list()
        logger.success(
            f"Bounce list reloaded successfully. Loaded {bounce_count} emails."
        )
    except Exception as e:
        logger.error(f"Error reloading bounce list: {str(e)}")
        raise typer.Exit(1)


@app.command()
def bounce_stats():
    """Show bounce list statistics"""
    try:
        pipeline = ValidationPipeline()
        stats = pipeline.get_bounce_list_stats()

        logger.info("Bounce List Statistics:")
        logger.info(f"  Total bounce emails: {stats['bounce_count']}")
        logger.info(f"  Loaded in memory: {stats['loaded_in_memory']}")

    except Exception as e:
        logger.error(f"Error getting bounce list statistics: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
