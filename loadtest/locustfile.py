import csv
import os
import random
from typing import List
from locust import HttpUser, task, between, events
from locust.exception import StopUser


class EmailValidatorUser(HttpUser):
    """Load test user for email validation API"""
    
    # Wait between 1-3 seconds between requests
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user with test data and authentication"""
        self.emails = self.load_test_emails()
        self.access_token = self.get_access_token()
        
        if not self.emails:
            print("ERROR: No test emails loaded. Please ensure 'test_emails_10k.csv' exists in loadtest/ directory.")
            events.request.fire(
                request_type="ERROR",
                name="No test data",
                response_time=0,
                response_length=0,
                exception=Exception("No test emails available")
            )
            raise StopUser()
    
    def load_test_emails(self) -> List[str]:
        """Load test emails from CSV file"""
        csv_path = os.path.join(os.path.dirname(__file__), "test_emails_10k.csv")
        
        if not os.path.exists(csv_path):
            print(f"WARNING: Test file not found at {csv_path}")
            print("Creating sample test data...")
            self.create_sample_test_data(csv_path)
        
        emails = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Skip header if present
                first_row = next(reader, None)
                if first_row and 'email' in first_row[0].lower():
                    # Header row, continue reading
                    pass
                else:
                    # No header, add back the first row
                    emails.append(first_row[0] if first_row else "")
                
                # Read remaining rows
                for row in reader:
                    if row and row[0].strip():
                        emails.append(row[0].strip())
            
            print(f"Loaded {len(emails)} test emails")
            return emails
            
        except Exception as e:
            print(f"ERROR loading test emails: {e}")
            return []
    
    def create_sample_test_data(self, csv_path: str):
        """Create sample test data if the CSV doesn't exist"""
        sample_emails = [
            "test1@example.com",
            "user@domain.com", 
            "admin@company.org",
            "support@service.net",
            "info@website.co.uk",
            "contact@business.com",
            "sales@enterprise.io",
            "help@platform.dev",
            "noreply@system.local",
            "webmaster@site.info"
        ]
        
        # Generate 10k emails by repeating and modifying the sample
        emails = []
        for i in range(10000):
            base_email = sample_emails[i % len(sample_emails)]
            name, domain = base_email.split('@')
            emails.append(f"{name}{i}@{domain}")
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['email'])  # Header
                for email in emails:
                    writer.writerow([email])
            print(f"Created sample test data with {len(emails)} emails at {csv_path}")
        except Exception as e:
            print(f"ERROR creating sample data: {e}")
    
    def get_access_token(self) -> str:
        """Get access token for API authentication"""
        try:
            # Try to get token using API key (if available)
            api_key = os.getenv('API_TOKEN', 'test-key')
            response = self.client.post("/token", json={"api_key": api_key})
            
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                print(f"WARNING: Failed to get token with API key: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"WARNING: Could not get access token: {e}")
            return ""
    
    @task(3)
    def validate_single_email(self):
        """Test single email validation (most common scenario)"""
        if not self.emails:
            return
            
        email = random.choice(self.emails)
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        
        payload = {
            "emails": [email],
            "enable_smtp": False,
            "enable_catch_all": False
        }
        
        with self.client.post(
            "/validate",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "results" in result and len(result["results"]) > 0:
                    response.success()
                else:
                    response.failure("No validation results returned")
            elif response.status_code == 401:
                response.failure("Authentication failed")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def validate_multiple_emails(self):
        """Test batch email validation"""
        if not self.emails:
            return
            
        # Select 5-10 random emails for batch validation
        batch_size = random.randint(5, 10)
        batch_emails = random.sample(self.emails, min(batch_size, len(self.emails)))
        
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        
        payload = {
            "emails": batch_emails,
            "enable_smtp": random.choice([True, False]),
            "enable_catch_all": random.choice([True, False])
        }
        
        with self.client.post(
            "/validate",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "results" in result and len(result["results"]) == len(batch_emails):
                    response.success()
                else:
                    response.failure("Batch validation results mismatch")
            elif response.status_code == 401:
                response.failure("Authentication failed")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def validate_with_advanced_options(self):
        """Test validation with SMTP and catch-all detection enabled"""
        if not self.emails:
            return
            
        email = random.choice(self.emails)
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        
        payload = {
            "emails": [email],
            "enable_smtp": True,
            "enable_catch_all": True
        }
        
        with self.client.post(
            "/validate",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "results" in result and len(result["results"]) > 0:
                    response.success()
                else:
                    response.failure("No validation results returned")
            elif response.status_code == 401:
                response.failure("Authentication failed")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Unexpected status: {response.status_code}")


# Optional: Add custom event listeners for detailed monitoring
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response and response.status_code >= 400:
        print(f"Request error: {name} - Status: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🚀 Starting Email Validator Load Test")
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.user_count if environment.runner else 'Not specified'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("🏁 Email Validator Load Test completed") 