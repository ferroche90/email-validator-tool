import csv
import os
from pathlib import Path
from typing import List
from loguru import logger
from email_validator_tool.core.models import ValidationResult

class EmailLoader:
    """Loader for email addresses from CSV files and efficient result writing."""
    
    @staticmethod
    def load_emails_from_csv(file_path: str) -> List[str]:
        """
        Load emails from a CSV file.
        
        Args:
            file_path: Path to the CSV file containing emails
            
        Returns:
            List of email addresses
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        try:
            emails = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Skip header if exists
                next(reader, None)
                for row in reader:
                    if row and row[0].strip():  # Check if row is not empty and email is not just whitespace
                        emails.append(row[0].strip())
            
            logger.info(f"Loaded {len(emails)} emails from {file_path}")
            return emails
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def write_csv_header(file_path: str):
        """
        Create a new CSV file and write the header row.
        
        Args:
            file_path: Path where to create the CSV file
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Email', 'Status', 'Details'])
            
            logger.info(f"Created CSV file with header: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating CSV file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def append_result_to_csv(result: ValidationResult, file_path: str):
        """
        Append a single validation result to the CSV file.
        Forces immediate write to disk for real-time visibility.
        
        Args:
            result: ValidationResult object to append
            file_path: Path to the CSV file
        """
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result.email,
                    result.status.value,
                    result.details or ''
                ])
                # Force immediate write to disk for real-time visibility
                f.flush()
                os.fsync(f.fileno())
            
            logger.debug(f"Appended result for {result.email} to {file_path}")
            
        except Exception as e:
            logger.error(f"Error appending result to CSV file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def write_results_to_csv(results: List[ValidationResult], file_path: str):
        """
        Write validation results to a CSV file (legacy method for backward compatibility).
        
        Args:
            results: List of ValidationResult objects
            file_path: Path where to write the CSV file
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Email', 'Status', 'Details'])
                # Write results
                for result in results:
                    writer.writerow([
                        result.email,
                        result.status.value,
                        result.details or ''
                    ])
            
            logger.info(f"Wrote {len(results)} results to {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing results to CSV file {file_path}: {str(e)}")
            raise
