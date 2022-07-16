#!/usr/bin/env python3
"""
Base Authentication Patterns for MCP Servers
Common authentication mechanisms used across different services
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAuthHandler(ABC):
    """Abstract base class for authentication handlers"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config_dir = Path.home() / f".{service_name}-mcp"
        self.config_dir.mkdir(exist_ok=True)

    @abstractmethod
    def authenticate(self) -> bool:
        """Perform authentication

        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated

        Returns:
            True if authenticated
        """
        pass

    def save_config(self, config: dict, filename: str = "config.json"):
        """Save configuration to file

        Args:
            config: Configuration dictionary
            filename: Config file name
        """
        config_file = self.config_dir / filename
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {config_file}")

    def load_config(self, filename: str = "config.json") -> Optional[dict]:
        """Load configuration from file

        Args:
            filename: Config file name

        Returns:
            Configuration dict or None if not found
        """
        config_file = self.config_dir / filename
        if not config_file.exists():
            return None

        with open(config_file, 'r') as f:
            return json.load(f)


class OAuth2Handler(BaseAuthHandler):
    """OAuth 2.0 authentication handler (like Gmail)"""

    def __init__(self, service_name: str, scopes: list, client_secrets_file: str):
        """Initialize OAuth2 handler

        Args:
            service_name: Service name
            scopes: OAuth scopes required
            client_secrets_file: Path to client secrets JSON
        """
        super().__init__(service_name)
        self.scopes = scopes
        self.client_secrets_file = client_secrets_file
        self.token_file = self.config_dir / "token.json"
        self.creds = None

    def authenticate(self) -> bool:
        """Perform OAuth2 authentication

        Returns:
            True if authentication successful
        """
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        # Load existing credentials
        if self.token_file.exists():
            self.creds = Credentials.from_authorized_user_file(
                str(self.token_file),
                self.scopes
            )

        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file,
                    self.scopes
                )
                self.creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())

        return self.creds is not None

    def is_authenticated(self) -> bool:
        """Check if authenticated

        Returns:
            True if authenticated
        """
        return self.creds is not None and self.creds.valid


class TokenAuthHandler(BaseAuthHandler):
    """Token-based authentication (like Zabbix, many REST APIs)"""

    def __init__(self, service_name: str, api_url: str):
        """Initialize token auth handler

        Args:
            service_name: Service name
            api_url: API base URL
        """
        super().__init__(service_name)
        self.api_url = api_url
        self.token = None
        self.token_file = self.config_dir / "auth_token.txt"

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and get token

        Args:
            username: Username
            password=REDACTED_PASSWORD

        Returns:
            True if authentication successful
        """
        # This is a template - implement specific API call
        # Example for JSON-RPC like Zabbix:
        import requests

        try:
            response = requests.post(
                self.api_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "username": username,
                        "password": password
                    },
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            if "result" in result:
                self.token = result["result"]
                self._save_token()
                return True

            return False

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def load_token(self) -> bool:
        """Load existing token

        Returns:
            True if token loaded
        """
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                self.token = f.read().strip()
            return True
        return False

    def _save_token(self):
        """Save token to file"""
        with open(self.token_file, 'w') as f:
            f.write(self.token)

    def is_authenticated(self) -> bool:
        """Check if authenticated

        Returns:
            True if authenticated
        """
        return self.token is not None


class BasicAuthHandler(BaseAuthHandler):
    """Basic authentication (username/password)"""

    def __init__(self, service_name: str, api_url: str):
        """Initialize basic auth handler

        Args:
            service_name: Service name
            api_url: API base URL
        """
        super().__init__(service_name)
        self.api_url = api_url
        self.username = None
        self.password = None
        self.creds_file = self.config_dir / "credentials.json"

    def authenticate(self, username: str, password: str) -> bool:
        """Set credentials

        Args:
            username: Username
            password=REDACTED_PASSWORD

        Returns:
            True if credentials set
        """
        self.username = username
        self.password=REDACTED_PASSWORD
        self._save_credentials()
        return True

    def load_credentials(self) -> bool:
        """Load credentials from file

        Returns:
            True if loaded successfully
        """
        if self.creds_file.exists():
            creds = self.load_config("credentials.json")
            if creds:
                self.username = creds.get("username")
                self.password=REDACTED_PASSWORDpassword")
                return True
        return False

    def _save_credentials(self):
        """Save credentials to file"""
        self.save_config({
            "username": self.username,
            "password": self.password
        }, "credentials.json")

    def is_authenticated(self) -> bool:
        """Check if authenticated

        Returns:
            True if credentials available
        """
        return self.username is not None and self.password is not None

    def get_auth_tuple(self) -> tuple:
        """Get auth tuple for requests

        Returns:
            (username, password) tuple
        """
        return (self.username, self.password)


# Factory function to create appropriate auth handler
def create_auth_handler(auth_type: str, service_name: str, **kwargs) -> BaseAuthHandler:
    """Create authentication handler based on type

    Args:
        auth_type: Type of auth ('oauth2', 'token', 'basic')
