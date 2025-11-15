# Secrets Management Production

Production-grade secrets management for cryptocurrency trading systems.

## AWS Secrets Manager Integration

```python
import boto3
import json
from typing import Dict, Optional
from functools import lru_cache
from datetime import datetime, timedelta

class SecretsManager:
    """
    AWS Secrets Manager integration for production secrets
    NEVER use python-dotenv or environment variables in production!
    """

    def __init__(
        self,
        region_name: str = 'us-east-1',
        cache_ttl_seconds: int = 300  # 5 minutes
    ):
        self.client = boto3.client('secretsmanager', region_name=region_name)
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache = {}
        self._cache_timestamps = {}

    async def get_secret(self, secret_name: str, force_refresh: bool = False) -> Dict:
        """
        Retrieve secret from AWS Secrets Manager with local caching

        Args:
            secret_name: Name of secret in AWS Secrets Manager
            force_refresh: Bypass cache and fetch fresh secret

        Returns:
            Secret data as dictionary
        """
        # Check cache first (unless force refresh)
        if not force_refresh and secret_name in self._cache:
            cache_age = datetime.utcnow() - self._cache_timestamps[secret_name]

            if cache_age < self.cache_ttl:
                logger.debug(f"Using cached secret: {secret_name}")
                return self._cache[secret_name]

        # Fetch from AWS
        try:
            logger.info(f"Fetching secret from AWS: {secret_name}")

            response = self.client.get_secret_value(SecretId=secret_name)

            # Parse secret
            if 'SecretString' in response:
                secret_data = json.loads(response['SecretString'])
            else:
                secret_data = json.loads(response['SecretBinary'].decode('utf-8'))

            # Update cache
            self._cache[secret_name] = secret_data
            self._cache_timestamps[secret_name] = datetime.utcnow()

            return secret_data

        except self.client.exceptions.ResourceNotFoundException:
            logger.error(f"Secret not found: {secret_name}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise

    async def get_exchange_credentials(self, exchange_id: str) -> Dict:
        """
        Retrieve exchange API credentials

        Secret format in AWS Secrets Manager:
        {
            "api_key": "...",
            "secret": "...",
            "passphrase": "...",  // Optional (for some exchanges)
            "subaccount": "..."   // Optional
        }
        """
        secret_name = f"trading-bot/{exchange_id}/credentials"
        return await self.get_secret(secret_name)

    async def get_telegram_token(self) -> str:
        """Retrieve Telegram bot token"""
        secret = await self.get_secret("trading-bot/telegram/token")
        return secret['token']

    async def get_database_credentials(self) -> Dict:
        """Retrieve database credentials"""
        return await self.get_secret("trading-bot/database/credentials")

    async def rotate_exchange_credentials(
        self,
        exchange_id: str,
        new_api_key: str,
        new_secret: str,
        new_passphrase: Optional[str] = None
    ):
        """
        Rotate exchange API credentials

        Steps:
        1. Create new credentials on exchange
        2. Update AWS Secrets Manager
        3. Wait for cache expiry or force refresh
        4. Revoke old credentials on exchange
        """
        secret_name = f"trading-bot/{exchange_id}/credentials"

        # Prepare new secret
        new_secret_data = {
            "api_key": new_api_key,
            "secret": new_secret,
        }

        if new_passphrase:
            new_secret_data["passphrase"] = new_passphrase

        # Update secret in AWS
        try:
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_secret_data)
            )

            logger.info(f"Rotated credentials for {exchange_id}")

            # Force cache refresh
            await self.get_secret(secret_name, force_refresh=True)

        except Exception as e:
            logger.error(f"Failed to rotate credentials for {exchange_id}: {e}")
            raise
```

## Secrets Rotation Automation

```python
from datetime import datetime, timedelta

class SecretsRotationManager:
    """
    Automate secrets rotation for compliance and security
    Rotate exchange API keys every 90 days
    """

    def __init__(self, secrets_manager: SecretsManager, exchange_connector):
        self.secrets = secrets_manager
        self.exchange = exchange_connector
        self.rotation_interval_days = 90

    async def check_rotation_needed(self, exchange_id: str) -> bool:
        """Check if credentials need rotation based on age"""
        secret_name = f"trading-bot/{exchange_id}/credentials"

        try:
            response = self.secrets.client.describe_secret(SecretId=secret_name)

            last_changed = response.get('LastChangedDate')
            if not last_changed:
                last_changed = response.get('CreatedDate')

            age = datetime.utcnow() - last_changed.replace(tzinfo=None)

            return age > timedelta(days=self.rotation_interval_days)

        except Exception as e:
            logger.error(f"Failed to check rotation status for {exchange_id}: {e}")
            return False

    async def rotate_credentials(self, exchange_id: str):
        """
        Fully automated credential rotation

        Steps:
        1. Create new API key on exchange
        2. Update AWS Secrets Manager
        3. Test new credentials
        4. Delete old API key from exchange
        """
        logger.info(f"Starting credential rotation for {exchange_id}")

        try:
            # Step 1: Create new API key on exchange (exchange-specific)
            # Most exchanges require manual creation via UI or support ticket
            # Some exchanges (e.g., FTX) support programmatic API key creation
            logger.warning(
                f"Credential rotation for {exchange_id} requires manual API key creation. "
                "Create new API key via exchange UI, then call rotate_exchange_credentials()"
            )

            # For exchanges that support programmatic creation:
            # new_key = await self.exchange.create_api_key(permissions=['read', 'trade'])

            # Step 2-3: Update and test (done in rotate_exchange_credentials)

        except Exception as e:
            logger.error(f"Credential rotation failed for {exchange_id}: {e}")
            raise

    async def audit_all_credentials(self) -> Dict:
        """Audit all stored credentials and check rotation status"""
        audit_report = {
            'timestamp': datetime.utcnow(),
            'credentials': []
        }

        # List all secrets with prefix "trading-bot/"
        paginator = self.secrets.client.get_paginator('list_secrets')

        for page in paginator.paginate(
            Filters=[{'Key': 'name', 'Values': ['trading-bot/']}]
        ):
            for secret in page['SecretList']:
                secret_name = secret['Name']
                last_changed = secret.get('LastChangedDate', secret.get('CreatedDate'))
                age = datetime.utcnow() - last_changed.replace(tzinfo=None)

                audit_report['credentials'].append({
                    'name': secret_name,
                    'age_days': age.days,
                    'last_changed': last_changed.isoformat(),
                    'rotation_needed': age.days > self.rotation_interval_days
                })

        return audit_report
```

## CloudHSM for High-Value Secrets

```python
import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CloudHSMSecretsManager:
    """
    AWS CloudHSM integration for ultra-high security (cold wallet keys, etc.)
    Cost: ~$1,200/month but provides FIPS 140-2 Level 3 hardware security
    """

    def __init__(self, cluster_id: str):
        self.cloudhsm = boto3.client('cloudhsmv2')
        self.cluster_id = cluster_id

    async def encrypt_cold_wallet_key(self, private_key: str) -> bytes:
        """
        Encrypt cold wallet private key using CloudHSM
        Private key NEVER leaves HSM in plaintext
        """
        # This is a simplified example
        # Real implementation uses CloudHSM SDK and requires HSM client setup

        logger.info("Encrypting cold wallet key in CloudHSM")

        # CloudHSM encryption happens inside hardware module
        # Returns encrypted blob that can only be decrypted by HSM

        # Placeholder - actual implementation requires CloudHSM client library
        return b"encrypted_key_blob"

    async def sign_transaction_with_hsm(
        self,
        transaction_data: bytes,
        key_label: str
    ) -> bytes:
        """
        Sign transaction using private key stored in HSM
        Private key NEVER leaves HSM
        """
        logger.info(f"Signing transaction with HSM key: {key_label}")

        # CloudHSM performs signing inside hardware module
        # Returns signature without exposing private key

        # Placeholder - actual implementation requires CloudHSM client library
        return b"transaction_signature"
```

## IP Whitelisting and API Key Restrictions

```python
class ExchangeSecurityConfig:
    """
    Security configuration for exchange API keys
    CRITICAL: Always restrict API keys
    """

    @staticmethod
    def get_recommended_restrictions() -> Dict:
        """
        Recommended security restrictions for exchange API keys

        CRITICAL RULES:
        1. NEVER enable withdrawal permissions on bot API keys
        2. ALWAYS whitelist server IP addresses
        3. ALWAYS restrict to spot/futures trading only
        4. ALWAYS set daily withdrawal limit to $0
        """
        return {
            'permissions': {
                'read': True,           # Read account data
                'trade': True,          # Place/cancel orders
                'withdraw': False,      # ❌ NEVER enable!
                'transfer': False,      # ❌ NEVER enable!
            },
            'ip_whitelist': [
                '52.1.2.3',             # Production server 1
                '52.1.2.4',             # Production server 2 (HA)
            ],
            'restrictions': {
                'spot_trading': True,
                'margin_trading': True,
                'futures_trading': True,
                'daily_withdrawal_limit_usd': 0,  # ❌ MUST be 0
            }
        }

    @staticmethod
    def audit_api_key_security(exchange_id: str, api_key_info: Dict) -> List[str]:
        """
        Audit API key configuration and return security warnings

        Returns: List of security warnings (empty if all good)
        """
        warnings = []

        # Check withdrawal permission
        if api_key_info.get('permissions', {}).get('withdraw', False):
            warnings.append(
                "🚨 CRITICAL: Withdrawal permission enabled! "
                "Disable immediately to prevent theft."
            )

        # Check IP whitelist
        if not api_key_info.get('ip_whitelist'):
            warnings.append(
                "⚠️  WARNING: No IP whitelist configured. "
                "Add server IPs to prevent unauthorized access."
            )

        # Check transfer permission
        if api_key_info.get('permissions', {}).get('transfer', False):
            warnings.append(
                "🚨 CRITICAL: Transfer permission enabled! "
                "Disable to prevent fund transfers."
            )

        # Check daily withdrawal limit
        withdrawal_limit = api_key_info.get('daily_withdrawal_limit_usd', 0)
        if withdrawal_limit > 0:
            warnings.append(
                f"⚠️  WARNING: Daily withdrawal limit is ${withdrawal_limit}. "
                "Set to $0 for bot API keys."
            )

        return warnings
```

## Secret Audit Logging

```python
import hashlib
from dataclasses import dataclass

@dataclass
class SecretAccessLog:
    timestamp: datetime
    secret_name: str
    accessed_by: str
    access_type: str  # 'read', 'write', 'rotate'
    ip_address: str
    success: bool

class SecretAuditLogger:
    """
    Comprehensive audit logging for all secret access
    Required for SOC 2 compliance
    """

    def __init__(self, s3_bucket: str):
        self.s3 = boto3.client('s3')
        self.bucket = s3_bucket
        self.log_buffer = []

    async def log_secret_access(
        self,
        secret_name: str,
        accessed_by: str,
        access_type: str,
        ip_address: str,
        success: bool
    ):
        """Log secret access event"""
        log_entry = SecretAccessLog(
            timestamp=datetime.utcnow(),
            secret_name=secret_name,
            accessed_by=accessed_by,
            access_type=access_type,
            ip_address=ip_address,
            success=success
        )

        # Add to buffer
        self.log_buffer.append(log_entry)

        # Log to CloudWatch
        logger.info(
            f"Secret access: {secret_name} by {accessed_by} "
            f"({access_type}) from {ip_address} - "
            f"{'SUCCESS' if success else 'FAILED'}"
        )

        # Flush buffer to S3 if needed
        if len(self.log_buffer) >= 100:
            await self._flush_to_s3()

    async def _flush_to_s3(self):
        """Flush audit logs to S3 (WORM storage for compliance)"""
        if not self.log_buffer:
            return

        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"secret-audit-logs/{timestamp}.jsonl"

        # Convert to JSONL
        log_data = '\n'.join(
            json.dumps({
                'timestamp': log.timestamp.isoformat(),
                'secret_name': log.secret_name,
                'accessed_by': log.accessed_by,
                'access_type': log.access_type,
                'ip_address': log.ip_address,
                'success': log.success
            })
            for log in self.log_buffer
        )

        # Upload to S3 with object lock (WORM - Write Once Read Many)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=log_data.encode('utf-8'),
            ServerSideEncryption='AES256',
            ObjectLockMode='COMPLIANCE',
            ObjectLockRetainUntilDate=datetime.utcnow() + timedelta(days=2555)  # 7 years
        )

        logger.info(f"Flushed {len(self.log_buffer)} audit logs to S3: {filename}")

        # Clear buffer
        self.log_buffer = []
```

---
**CRITICAL for production**: Never use .env files or environment variables for secrets. Always use AWS Secrets Manager + CloudHSM for production deployments.
