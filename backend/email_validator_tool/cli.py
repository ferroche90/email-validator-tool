import asyncio
from pathlib import Path

import typer
from loguru import logger
from tabulate import tabulate

from email_validator_tool.config import update_settings
from email_validator_tool.core.loader import EmailLoader
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import generate_summary
from email_validator_tool.key_manager import create_key_manager, generate_jwt_for_key

app = typer.Typer(
    name="email-validator",
    help="Email validator with multiple verification layers",
    add_completion=False,
)

# Create sub-app for key management
keys_app = typer.Typer(help="Manage API keys")
app.add_typer(keys_app, name="manage-keys")


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

        logger.info(f"Configuration: ENABLE_CATCH_ALL={settings.ENABLE_CATCH_ALL}, ENABLE_SMTP={settings.ENABLE_SMTP}")

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
                    logger.info(f"Progress: {processed_count}/{len(emails)} emails processed and saved to CSV")

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
        logger.success(f"DNS cache cleared successfully. Removed {removed_count} entries.")
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
        logger.success(f"Expired cache entries cleaned up. Removed {removed_count} entries.")
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}")
        raise typer.Exit(1)


@app.command()
def reload_bounce_list():
    """Reload the bounce list from the database"""
    try:
        pipeline = ValidationPipeline()
        bounce_count = pipeline.reload_bounce_list()
        logger.success(f"Bounce list reloaded successfully. Loaded {bounce_count} emails.")
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


@keys_app.command()
def create(role: str = typer.Argument(..., help="Role for the API key (user or admin)", case_sensitive=False)):
    """Create a new API key with the specified role."""
    try:
        if role.lower() not in ["user", "admin"]:
            typer.echo("Error: Role must be 'user' or 'admin'", err=True)
            raise typer.Exit(1)

        key_manager = create_key_manager()
        api_key = key_manager.create_key(role.lower())

        # Generate JWT token
        jwt_token = generate_jwt_for_key(api_key.key, api_key.role)

        typer.echo(f"\n✅ API Key created successfully!")
        typer.echo(f"Role: {api_key.role}")
        typer.echo(f"API Key: {api_key.key}")
        typer.echo(f"JWT Token: {jwt_token}")
        typer.echo(f"Created: {api_key.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        typer.echo("\n💡 Use the API key for authentication or the JWT token for direct access.")

    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise typer.Exit(1)


@keys_app.command()
def list():
    """List all API keys with their status."""
    try:
        key_manager = create_key_manager()
        keys = key_manager.list_keys()

        if not keys:
            typer.echo("No API keys found.")
            return

        # Prepare table data
        table_data = []
        for key in keys:
            status = "🟢 Active" if not key.revoked else "🔴 Revoked"
            table_data.append(
                [
                    key.key[:16] + "..." if len(key.key) > 16 else key.key,
                    key.role,
                    status,
                    key.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        # Display table
        headers = ["API Key", "Role", "Status", "Created At"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        typer.echo(table)

    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        raise typer.Exit(1)


@keys_app.command()
def revoke(key: str = typer.Argument(..., help="API key to revoke (can be partial, will match first 16 characters)")):
    """Revoke an API key."""
    try:
        key_manager = create_key_manager()

        # Find the key (support partial matching)
        target_key = None
        for stored_key in key_manager.keys.keys():
            if stored_key.startswith(key) or stored_key == key:
                target_key = stored_key
                break

        if not target_key:
            typer.echo(f"Error: API key '{key}' not found", err=True)
            raise typer.Exit(1)

        # Check if already revoked
        key_info = key_manager.get_key_info(target_key)
        if key_info and key_info.revoked:
            typer.echo(f"API key '{target_key[:16]}...' is already revoked.")
            return

        # Revoke the key
        if key_manager.revoke_key(target_key):
            typer.echo(f"✅ API key '{target_key[:16]}...' has been revoked.")
        else:
            typer.echo(f"Error: Failed to revoke API key '{key}'", err=True)
            raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
