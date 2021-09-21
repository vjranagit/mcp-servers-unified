#!/usr/bin/env python3
"""
Enhanced Gmail MCP Server
Provides comprehensive Gmail integration with advanced features
Version: 2.1
"""

__version__ = "2.1.0"

import json
import base64
import asyncio
from pathlib import Path
from typing import Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Gmail credentials path
TOKEN_FILE = Path.home() / ".gmail-mcp/token.json"

def get_gmail_service():
    """Get authenticated Gmail service"""
    if not TOKEN_FILE.exists():
        raise Exception("No token file found. Authentication required.")

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def search_emails(query: str = "is:unread", max_results: int = 10) -> dict:
    """Search Gmail messages"""
    service = get_gmail_service()

    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return {"status": "success", "count": 0, "messages": []}

        email_list = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = msg_data['payload'].get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            is_unread = 'UNREAD' in msg_data.get('labelIds', [])

            email_list.append({
                "id": msg['id'],
                "subject": subject,
                "from": from_addr,
                "date": date,
                "unread": is_unread
            })

        return {
            "status": "success",
            "count": len(email_list),
            "query": query,
            "messages": email_list
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def get_email_body(msg_payload):
    """Extract email body from message payload"""
    body = ""

    if 'parts' in msg_payload:
        for part in msg_payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    elif 'body' in msg_payload and 'data' in msg_payload['body']:
        body = base64.urlsafe_b64decode(msg_payload['body']['data']).decode('utf-8')

    return body

def read_email(message_id: str) -> dict:
    """Read full email content by message ID"""
    service = get_gmail_service()

    try:
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        headers = msg['payload'].get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        to_addr = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown')

        body = get_email_body(msg['payload'])

        # Truncate body if too long
        if len(body) > 5000:
            body = body[:5000] + "\n\n... (truncated)"

        return {
            "status": "success",
            "message_id": message_id,
            "subject": subject,
            "from": from_addr,
            "to": to_addr,
            "date": date,
            "body": body,
            "labels": msg.get('labelIds', [])
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def send_email(to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> dict:
    """Send an email"""
    service = get_gmail_service()

    try:
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        return {
            "status": "success",
            "message_id": sent_message['id'],
            "to": to,
            "subject": subject
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def mark_as_read(message_id: str) -> dict:
    """Mark an email as read"""
    service = get_gmail_service()

    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "action": "marked_as_read"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def mark_as_unread(message_id: str) -> dict:
    """Mark an email as unread"""
    service = get_gmail_service()

    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': ['UNREAD']}
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "action": "marked_as_unread"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def delete_email(message_id: str) -> dict:
    """Move an email to trash"""
    service = get_gmail_service()

    try:
        service.users().messages().trash(
            userId='me',
            id=message_id
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "action": "moved_to_trash"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def archive_email(message_id: str) -> dict:
    """Archive an email (remove from inbox)"""
    service = get_gmail_service()

    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['INBOX']}
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "action": "archived"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def star_email(message_id: str, star: bool = True) -> dict:
    """Star or unstar an email"""
    service = get_gmail_service()

    try:
        if star:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            action = "starred"
        else:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['STARRED']}
            ).execute()
            action = "unstarred"

        return {
            "status": "success",
