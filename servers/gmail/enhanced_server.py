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
            "message_id": message_id,
            "action": action
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def list_labels() -> dict:
    """List all Gmail labels"""
    service = get_gmail_service()

    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        label_list = [{
            "id": label['id'],
            "name": label['name'],
            "type": label.get('type', 'user')
        } for label in labels]

        return {
            "status": "success",
            "count": len(label_list),
            "labels": label_list
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def add_label(message_id: str, label_id: str) -> dict:
    """Add a label to an email"""
    service = get_gmail_service()

    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "label_id": label_id,
            "action": "label_added"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def remove_label(message_id: str, label_id: str) -> dict:
    """Remove a label from an email"""
    service = get_gmail_service()

    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': [label_id]}
        ).execute()

        return {
            "status": "success",
            "message_id": message_id,
            "label_id": label_id,
            "action": "label_removed"
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def create_draft(to: str, subject: str, body: str) -> dict:
    """Create a draft email"""
    service = get_gmail_service()

    try:
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()

        return {
            "status": "success",
            "draft_id": draft['id'],
            "message_id": draft['message']['id'],
            "to": to,
            "subject": subject
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def reply_to_email(message_id: str, body: str) -> dict:
    """Reply to an email"""
    service = get_gmail_service()

    try:
        from email.mime.text import MIMEText

        # Get original message
        original = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Message-ID']
        ).execute()

        headers = original['payload'].get('headers', [])
        original_from = next((h['value'] for h in headers if h['name'] == 'From'), '')
        original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        message_id_header = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')

        # Extract email from "Name <email>" format
        import re
        email_match = re.search(r'<(.+?)>', original_from)
        to_email = email_match.group(1) if email_match else original_from

        # Create reply
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        message['In-Reply-To'] = message_id_header
        message['References'] = message_id_header

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        sent_message = service.users().messages().send(
            userId='me',
            body={
                'raw': raw_message,
                'threadId': original.get('threadId')
            }
        ).execute()

        return {
            "status": "success",
            "message_id": sent_message['id'],
            "thread_id": sent_message.get('threadId'),
            "replied_to": message_id
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def get_thread(thread_id: str) -> dict:
    """Get all messages in a thread/conversation"""
    service = get_gmail_service()

    try:
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()

        messages = []
        for msg in thread.get('messages', []):
            headers = msg['payload'].get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

            messages.append({
                "id": msg['id'],
                "subject": subject,
                "from": from_addr,
                "date": date
            })

        return {
            "status": "success",
            "thread_id": thread_id,
            "message_count": len(messages),
            "messages": messages
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def list_attachments(message_id: str) -> dict:
    """List all attachments in an email"""
    service = get_gmail_service()

    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        attachments = []

        def extract_attachments(parts):
            """Recursively extract attachments from message parts"""
            for part in parts:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    attachment_info = {
                        "filename": part['filename'],
                        "mimeType": part.get('mimeType', 'unknown'),
                        "size": part['body'].get('size', 0),
                        "attachmentId": part['body']['attachmentId']
                    }
                    attachments.append(attachment_info)

                # Recursively check nested parts
                if 'parts' in part:
                    extract_attachments(part['parts'])

        # Extract attachments from message payload
        payload = message.get('payload', {})
        if 'parts' in payload:
            extract_attachments(payload['parts'])

        return {
            "status": "success",
            "message_id": message_id,
            "attachment_count": len(attachments),
            "attachments": attachments
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

def download_attachment(message_id: str, attachment_id: str, filename: str, save_path: str = None) -> dict:
    """Download an email attachment"""
    service = get_gmail_service()

    try:
        # Get the attachment data
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()

        # Decode the attachment data
        file_data = base64.urlsafe_b64decode(attachment['data'])

        # Determine save path
        if not save_path:
            save_path = Path.home() / "Downloads" / filename
        else:
            save_path = Path(save_path) / filename

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(save_path, 'wb') as f:
            f.write(file_data)

        return {
            "status": "success",
            "message_id": message_id,
            "attachment_id": attachment_id,
            "filename": filename,
            "saved_to": str(save_path),
            "size_bytes": len(file_data)
        }

    except Exception as error:
        return {"status": "error", "message": str(error)}

# Create MCP server
app = Server("enhanced-gmail-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Gmail tools"""
    return [
        Tool(
            name="search_emails",
            description="Search Gmail messages using Gmail search syntax. Returns a list of matching emails with subject, from, date, and unread status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'is:unread', 'from:someone@example.com', 'subject:important')",
                        "default": "is:unread"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="read_email",
            description="Read the full content of an email by its message ID. Returns subject, from, to, date, and email body.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to read"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="send_email",
            description="Send an email to a recipient with a subject and body. Supports CC and BCC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC email addresses (optional)"
                    },
                    "bcc": {
                        "type": "string",
                        "description": "BCC email addresses (optional)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="mark_as_read",
            description="Mark an email as read by removing the UNREAD label.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to mark as read"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="mark_as_unread",
            description="Mark an email as unread by adding the UNREAD label.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to mark as unread"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="delete_email",
            description="Move an email to trash (can be recovered from trash).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to delete"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="archive_email",
            description="Archive an email by removing it from the inbox (removes INBOX label).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to archive"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="star_email",
            description="Star or unstar an email to mark it as important.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to star/unstar"
                    },
                    "star": {
                        "type": "boolean",
                        "description": "True to star, False to unstar",
                        "default": True
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="list_labels",
            description="List all Gmail labels (folders) available in the account.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="add_label",
            description="Add a label to an email message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID"
                    },
                    "label_id": {
                        "type": "string",
                        "description": "The label ID to add (use list_labels to get label IDs)"
                    }
                },
                "required": ["message_id", "label_id"]
            }
        ),
        Tool(
            name="remove_label",
            description="Remove a label from an email message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID"
                    },
                    "label_id": {
                        "type": "string",
                        "description": "The label ID to remove"
                    }
                },
                "required": ["message_id", "label_id"]
            }
        ),
        Tool(
            name="create_draft",
            description="Create a draft email that can be sent later.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="reply_to_email",
            description="Reply to an existing email message in the same thread.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to reply to"
                    },
                    "body": {
                        "type": "string",
                        "description": "Reply message body"
                    }
                },
                "required": ["message_id", "body"]
            }
        ),
        Tool(
            name="get_thread",
            description="Get all messages in an email thread/conversation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "The Gmail thread ID"
                    }
                },
                "required": ["thread_id"]
            }
        ),
        Tool(
            name="list_attachments",
            description="List all attachments in an email. Returns filename, MIME type, size, and attachment ID for each attachment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="download_attachment",
            description="Download an email attachment to local storage. By default saves to ~/Downloads folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID"
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "The attachment ID (from list_attachments)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "The filename to save the attachment as"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional custom directory path to save the attachment (defaults to ~/Downloads)"
                    }
                },
                "required": ["message_id", "attachment_id", "filename"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "search_emails":
        query = arguments.get("query", "is:unread")
        max_results = arguments.get("max_results", 10)
        result = search_emails(query, max_results)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "read_email":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = read_email(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "send_email":
        to = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        cc = arguments.get("cc")
        bcc = arguments.get("bcc")
        if not all([to, subject, body]):
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "to, subject, and body are required"}))]
        result = send_email(to, subject, body, cc, bcc)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "mark_as_read":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = mark_as_read(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "mark_as_unread":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = mark_as_unread(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "delete_email":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = delete_email(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "archive_email":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = archive_email(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "star_email":
        message_id = arguments.get("message_id")
        star = arguments.get("star", True)
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = star_email(message_id, star)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "list_labels":
        result = list_labels()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "add_label":
        message_id = arguments.get("message_id")
        label_id = arguments.get("label_id")
        if not all([message_id, label_id]):
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id and label_id are required"}))]
        result = add_label(message_id, label_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "remove_label":
        message_id = arguments.get("message_id")
        label_id = arguments.get("label_id")
        if not all([message_id, label_id]):
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id and label_id are required"}))]
        result = remove_label(message_id, label_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "create_draft":
        to = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        if not all([to, subject, body]):
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "to, subject, and body are required"}))]
        result = create_draft(to, subject, body)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "reply_to_email":
        message_id = arguments.get("message_id")
        body = arguments.get("body")
        if not all([message_id, body]):
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id and body are required"}))]
        result = reply_to_email(message_id, body)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_thread":
        thread_id = arguments.get("thread_id")
        if not thread_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "thread_id is required"}))]
        result = get_thread(thread_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "list_attachments":
        message_id = arguments.get("message_id")
        if not message_id:
            return [TextContent(type="text", text=json.dumps({"status": "error", "message": "message_id is required"}))]
        result = list_attachments(message_id)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

