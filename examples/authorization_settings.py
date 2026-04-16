import os
from config.constants import CLIENT_ID, CLIENT_SECRET, AUTH_SERVER, ISSUER, AUDIENCE, AUTHORIZATION_CODE, VERIFY_SSL, BASE_URI, TOKEN_URL, AUTHORIZATION_URL

"""
This file provides authentication settings for the Arium examples.
You can set these settings using environment variables.

### Instructions for setting environment variables:

#### Linux and macOS (Bash/Zsh):
1.  Open your terminal.
2.  Set the environment variable for the current session:
    ```bash
    export CLIENT_ID="your_client_id"
    export CLIENT_SECRET="your_client_secret"
    export AUTH_SERVER="your_auth_server"
    export ISSUER="your_issuer"
    export AUDIENCE="your_audience"
    export AUTHORIZATION_URL="your_authorization_url"
    export TOKEN_URL="your_token_url"
    export BASE_URI="your_base_uri"
    ```
3.  To make these changes permanent, add the `export` commands to your `~/.bashrc`, `~/.bash_profile`, or `~/.zshrc` file.

#### Windows (Command Prompt - cmd.exe):
1.  Open Command Prompt.
2.  Set the environment variable for the current session:
    ```cmd
    set CLIENT_ID=your_client_id
    set CLIENT_SECRET=your_client_secret
    set AUTH_SERVER=your_auth_server
    set ISSUER=your_issuer
    set AUDIENCE=your_audience
    set AUTHORIZATION_URL=your_authorization_url
    set TOKEN_URL=your_token_url
    set BASE_URI=your_base_uri
    ```
3.  To make these changes permanent, use the `setx` command or go to "Edit the system environment variables" in the Control Panel.

#### Windows (PowerShell):
1.  Open PowerShell.
2.  Set the environment variable for the current session:
    ```powershell
    $env:CLIENT_ID = "your_client_id"
    $env:CLIENT_SECRET = "your_client_secret"
    $env:AUTH_SERVER = "your_auth_server"
    $env:ISSUER = "your_issuer"
    $env:AUDIENCE = "your_audience"
    $env:AUTHORIZATION_URL = "your_authorization_url"
    $env:TOKEN_URL = "your_token_url"
    $env:BASE_URI = "your_base_uri"
    ```
3.  To make these changes permanent, add these lines to your PowerShell profile ($PROFILE).
"""


def get_auth_m2m_settings() -> dict:
    return {
        CLIENT_ID: os.getenv("CLIENT_ID", ""),
        CLIENT_SECRET: os.getenv("CLIENT_SECRET", ""),
        AUTH_SERVER: os.getenv("AUTH_SERVER", ""),
        ISSUER: os.getenv("ISSUER", ""),
        AUDIENCE: os.getenv("AUDIENCE", ""),
        AUTHORIZATION_CODE: False,
        VERIFY_SSL: True
    }


def get_auth_m2m_settings_v2() -> dict:
    return {
        CLIENT_ID: os.getenv("CLIENT_ID", ""),
        CLIENT_SECRET: os.getenv("CLIENT_SECRET", ""),
        AUTHORIZATION_URL: os.getenv("AUTHORIZATION_URL", ""),
        TOKEN_URL: os.getenv("TOKEN_URL", ""),
        BASE_URI: os.getenv("BASE_URI", ""),
        AUTHORIZATION_CODE: False,
        VERIFY_SSL: True
    }


def get_auth_settings() -> dict:
    return {
        CLIENT_ID: os.getenv("CLIENT_ID", ""),
        CLIENT_SECRET: os.getenv("CLIENT_SECRET", ""),
        AUTHORIZATION_URL: os.getenv("AUTHORIZATION_URL", ""),
        TOKEN_URL: os.getenv("TOKEN_URL", ""),
        BASE_URI: os.getenv("BASE_URI", ""),
        AUTHORIZATION_CODE: True,
        VERIFY_SSL: True
    }
