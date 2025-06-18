import asyncio
from pathlib import Path
import typer
from loguru import logger

from email_validator_tool.config import Settings
from email_validator_tool.core.loader import EmailLoader
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import generate_summary

app = typer.Typer(
    name="email-validator",
    help="Validador de correos electrónicos con múltiples capas de verificación",
    add_completion=False
)

@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="Ruta al archivo CSV con los correos a validar",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_path: Path = typer.Argument(
        ...,
        help="Ruta donde guardar el CSV con los resultados",
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
    enable_catch_all: bool = typer.Option(
        False,
        "--enable-catch-all",
        help="Habilitar detección de catch-all (fase 2)",
    ),
    enable_smtp: bool = typer.Option(
        False,
        "--enable-smtp",
        help="Habilitar verificación SMTP (fase 3)",
    ),
):
    """
    Valida una lista de correos electrónicos aplicando múltiples capas de verificación.
    Los resultados se guardan en un archivo CSV y se muestra un resumen estadístico.
    """
    try:
        # Load configuration
        settings = Settings()
        if enable_catch_all:
            settings.ENABLE_CATCH_ALL = True
        if enable_smtp:
            settings.ENABLE_SMTP = True
        
        # Load emails
        logger.info(f"Cargando correos desde {input_path}")
        emails = EmailLoader.load_emails_from_csv(str(input_path))
        
        # Process emails and write results incrementally
        logger.info(f"Procesando {len(emails)} correos...")
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
        
        logger.success(f"Proceso completado. Resultados guardados en {output_path}")
        
    except Exception as e:
        logger.error(f"Error durante la validación: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
