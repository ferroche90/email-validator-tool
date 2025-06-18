from collections import Counter
from typing import List
from loguru import logger
from email_validator_tool.models import ValidationResult, ValidationStatus

def generate_summary(results: List[ValidationResult]) -> None:
    """
    Generate and display a statistical summary of validation results.
    
    Args:
        results: List of ValidationResult objects
    """
    if not results:
        logger.warning("No results to summarize")
        return
    
    # Count results by status
    status_counts = Counter(result.status for result in results)
    total = len(results)
    
    # Define status labels in Spanish
    status_labels = {
        ValidationStatus.VALID: "Válidos",
        ValidationStatus.INVALID_SYNTAX: "Sintaxis Inválida",
        ValidationStatus.INVALID_DOMAIN: "Dominio Inválido",
        ValidationStatus.INVALID_MX: "MX Inválido",
        ValidationStatus.DISPOSABLE: "Dominios Desechables",
        ValidationStatus.ROLE_ACCOUNT: "Cuentas de Rol",
        ValidationStatus.ON_BOUNCE_LIST: "En Lista de Rebotes",
        ValidationStatus.CATCH_ALL: "Catch-All",
        ValidationStatus.INVALID_SMTP: "SMTP Inválido",
        ValidationStatus.UNKNOWN_ERROR: "Errores Desconocidos"
    }
    
    # Print header
    logger.info("\n=== RESUMEN DE VALIDACIÓN ===")
    logger.info(f"Total de correos procesados: {total}")
    logger.info("-" * 40)
    
    # Print each status count and percentage
    for status in ValidationStatus:
        count = status_counts.get(status, 0)
        percentage = (count / total) * 100
        label = status_labels.get(status, status.value)
        logger.info(f"{label}: {count:,} ({percentage:.1f}%)")
    
    # Print footer
    logger.info("-" * 40)
    
    # Print some additional statistics
    valid_count = status_counts.get(ValidationStatus.VALID, 0)
    invalid_count = total - valid_count
    valid_percentage = (valid_count / total) * 100
    invalid_percentage = (invalid_count / total) * 100
    
    logger.info(f"\nCorreos válidos: {valid_count:,} ({valid_percentage:.1f}%)")
    logger.info(f"Correos inválidos: {invalid_count:,} ({invalid_percentage:.1f}%)")
