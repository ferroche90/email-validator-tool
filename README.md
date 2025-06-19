# Email Validator Tool

A professional command-line tool for validating email addresses through multiple verification layers, including syntax, DNS/MX, disposable domains, role accounts, bounce list, and optionally, catch-all detection and SMTP verification.

## Technology Stack

- **Python 3.8+**: Base language
- **email-validator**: RFC syntax validation
- **dnspython**: MX records verification
- **disposable-email-domains**: Disposable domain detection
- **aiosmtplib**: Asynchronous SMTP verification
- **Typer**: Command-line interface
- **Pydantic**: Data validation and configuration
- **Loguru**: Logging system
- **SQLite**: Local database for bounce list
- **pytest**: Testing framework
- **Black/isort/flake8**: Formatting and linting

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/email-validator-tool.git
   cd email-validator-tool
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Adjust variables in `.env`:
   ```
   CSV_INPUT_PATH=emails.csv
   CSV_OUTPUT_PATH=results.csv
   MAX_CONCURRENT_CONNECTIONS=10
   PER_DOMAIN_DELAY_SECONDS=5.0
   SMTP_TIMEOUT=10
   ENABLE_CATCH_ALL=False
   ENABLE_SMTP=False
   ```

## Usage

Validate a list of emails:
```bash
python -m email_validator_tool.cli input.csv output.csv
```

Enable catch-all verification (phase 2):
```bash
python -m email_validator_tool.cli input.csv output.csv --enable-catch-all
```

Enable SMTP verification (phase 3):
```bash
python -m email_validator_tool.cli input.csv output.csv --enable-smtp
```

## Validation Layers

1. **Syntax (RFC)**
   - Verifies email complies with RFC specification
   - Uses email-validator for robust validation

2. **DNS/MX**
   - Checks domain existence
   - Verifies valid MX records
   - Uses dnspython for DNS resolution

3. **Disposable Domains**
   - Detects temporary email domains
   - Uses disposable-email-domains dataset

4. **Role Accounts**
   - Identifies generic accounts (admin, info, etc.)
   - Uses custom patterns and common role account names

5. **Bounce List**
   - Verifies against local bounce database
   - Stores history in SQLite

6. **Catch-all** (Optional)
   - Detects domains that accept any email
   - Requires SMTP verification

7. **SMTP** (Optional)
   - Verifies actual mailbox existence
   - Requires direct server connection

## Risk Management

⚠️ **Warning**: SMTP and catch-all verifications are considered high-risk:

- May result in IP blocking by mail servers
- Should be used with caution and proper configuration
- Recommendations:
  - Use delays between verifications (PER_DOMAIN_DELAY_SECONDS)
  - Limit concurrent connections (MAX_CONCURRENT_CONNECTIONS)
  - Configure appropriate timeouts (SMTP_TIMEOUT)
  - Consider using a dedicated VPS
  - Implement IP rotation if necessary

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
