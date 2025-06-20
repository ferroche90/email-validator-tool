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
   git clone https://github.com/ferroche90/email-validator-tool.git
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
   ENABLE_DNS_CACHE=True
   DNS_CACHE_TTL_SECONDS=3600
   ```

## Usage

The tool provides several commands for email validation and system management:

### Main Validation Command

#### Validate Email List
```bash
python -m email_validator_tool.cli validate input.csv output.csv [OPTIONS]
```

**Options:**
- `--enable-catch-all`: Enable catch-all detection (phase 2)
- `--enable-smtp`: Enable SMTP verification (phase 3)

**Examples:**
```bash
# Basic validation
python -m email_validator_tool.cli validate emails.csv results.csv

# With catch-all detection
python -m email_validator_tool.cli validate emails.csv results.csv --enable-catch-all

# With SMTP verification
python -m email_validator_tool.cli validate emails.csv results.csv --enable-smtp

# With both advanced features
python -m email_validator_tool.cli validate emails.csv results.csv --enable-catch-all --enable-smtp
```

### DNS Cache Management Commands

#### View Cache Statistics
```bash
python -m email_validator_tool.cli cache-stats
```
Displays current DNS cache statistics including total entries, valid entries, expired entries, and cache TTL.

#### Clear DNS Cache
```bash
python -m email_validator_tool.cli clear-cache
```
Removes all cached DNS results. Useful when you want to force fresh DNS queries.

#### Clean Up Expired Cache Entries
```bash
python -m email_validator_tool.cli cleanup-cache
```
Removes only expired cache entries while keeping valid ones. This is automatically done periodically during validation.

### Bounce List Management Commands

#### Reload Bounce List
```bash
python -m email_validator_tool.cli reload-bounce-list
```
Reloads the bounce list from the SQLite database into memory. Use this when the database has been updated.

#### View Bounce List Statistics
```bash
python -m email_validator_tool.cli bounce-stats
```
Shows bounce list statistics including the number of bounce emails loaded in memory.

### Command Summary

| Command | Description | Use Case |
|---------|-------------|----------|
| `validate input.csv output.csv` | Main validation command | Validate email list |
| `cache-stats` | View DNS cache statistics | Monitor cache usage |
| `clear-cache` | Clear all DNS cache | Force fresh DNS queries |
| `cleanup-cache` | Remove expired cache entries | Clean up old cache data |
| `reload-bounce-list` | Reload bounce list from DB | Update bounce list |
| `bounce-stats` | View bounce list statistics | Monitor bounce list |

### Getting Help

To see all available commands:
```bash
python -m email_validator_tool.cli --help
```

To get help for a specific command:
```bash
python -m email_validator_tool.cli [COMMAND] --help
```

## DNS Cache Management

The tool includes an intelligent DNS caching system that stores MX record query results in memory to avoid repeated network requests for the same domains. This significantly improves performance when validating large lists with repeated domains.

### Cache Configuration

Add these settings to your `.env` file to configure the DNS cache:

```
ENABLE_DNS_CACHE=True
DNS_CACHE_TTL_SECONDS=3600
```

- `ENABLE_DNS_CACHE`: Enable/disable DNS caching (default: True)
- `DNS_CACHE_TTL_SECONDS`: Time to live for cached results in seconds (default: 3600 = 1 hour)

### Cache Behavior

- Cache entries include both successful MX records and error results (invalid domains, no MX records)
- Automatic cleanup occurs every 100 queries to remove expired entries
- Cache is domain-based, so different emails from the same domain share the same cache entry
- Cache persists for the duration of the validation session

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
