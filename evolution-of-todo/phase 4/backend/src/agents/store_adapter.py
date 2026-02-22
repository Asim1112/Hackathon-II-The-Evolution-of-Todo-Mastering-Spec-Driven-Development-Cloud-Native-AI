"""
ChatKit Store adapter over existing Conversation/Message models.

Maps ChatKit thread/item operations to the existing database schema
without requiring any schema changes. ThreadItems are serialized as JSON
in Message.content field.
"""

import json
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from sqlmodel import Session, select

from chatkit.store import Store, NotFoundError
from chatkit.types import (
    ThreadMetadata,
    Page,
    UserMessageItem,
    AssistantMessageItem,
    UserMessageTextContent,
    InferenceOptions,
)

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.database.session import get_session

logger = logging.getLogger(__name__)

# Type alias for ThreadItem union
ThreadItem = (
    UserMessageItem
    | AssistantMessageItem
)


@dataclass
class RequestContext:
    """Carry request-specific data for multi-tenancy isolation."""
    user_id: str


# ---------------------------------------------------------------------------
# Serialization Helpers
# ---------------------------------------------------------------------------

def serialize_thread_item(item) -> dict:
    """Convert a ThreadItem to a dict suitable for Message storage."""
    # Handle agents library items (MessageOutputItem, etc.) that wrap raw_item
    if hasattr(item, 'raw_item'):
        return item.raw_item.model_dump(mode="json")
    # Handle ChatKit items (UserMessageItem, AssistantMessageItem)
    return item.model_dump(mode="json")


def deserialize_thread_item(message: Message):
    """Convert a Message back to a ThreadItem."""
    try:
        data = json.loads(message.content)
    except (json.JSONDecodeError, TypeError):
        # Legacy plain-text messages: wrap in appropriate item type
        if message.role == MessageRole.USER or message.role == "user":
            return UserMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=message.created_at.replace(tzinfo=timezone.utc) if message.created_at.tzinfo is None else message.created_at,
                type="user_message",
                content=[UserMessageTextContent(type="input_text", text=message.content)],
                attachments=[],
                quoted_text=None,
                inference_options=InferenceOptions(),
            )
        else:
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=message.created_at.replace(tzinfo=timezone.utc) if message.created_at.tzinfo is None else message.created_at,
                type="assistant_message",
                content=[{"type": "output_text", "text": message.content}],
            )

    # New-format JSON messages: validate by type discriminator
    item_type = data.get("type")
    if item_type == "user_message":
        if "inference_options" not in data:
            data["inference_options"] = {}
        return UserMessageItem.model_validate(data)
    elif item_type == "assistant_message":
        return AssistantMessageItem.model_validate(data)
    else:
        # Fallback: treat as plain text based on role
        if message.role == MessageRole.USER or message.role == "user":
            return UserMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=message.created_at.replace(tzinfo=timezone.utc) if message.created_at.tzinfo is None else message.created_at,
                type="user_message",
                content=[UserMessageTextContent(type="input_text", text=message.content)],
                attachments=[],
                quoted_text=None,
                inference_options=InferenceOptions(),
            )
        else:
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=message.created_at.replace(tzinfo=timezone.utc) if message.created_at.tzinfo is None else message.created_at,
                type="assistant_message",
                content=[{"type": "output_text", "text": message.content}],
            )


def conversation_to_thread_metadata(conversation: Conversation) -> ThreadMetadata:
    """Convert Conversation model to ChatKit ThreadMetadata."""
    created = conversation.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return ThreadMetadata(
        id=str(conversation.id),
        created_at=created,
    )


# ---------------------------------------------------------------------------
# Store Adapter
# ---------------------------------------------------------------------------

class PostgresStoreAdapter(Store[RequestContext]):
    """
    ChatKit Store implementation backed by existing Conversation/Message models.

    All queries filter by context.user_id for multi-tenancy isolation.
    """

    def _get_session(self) -> Session:
        """Get a new database session."""
        gen = get_session()
        return next(gen)

    # -- Thread operations --------------------------------------------------

    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == context.user_id,
            )
            conversation = session.exec(stmt).first()
            if not conversation:
                raise NotFoundError(f"Thread {thread_id} not found")
            return conversation_to_thread_metadata(conversation)

    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        conversation_id = self._parse_thread_id(thread.id, context.user_id)
        with Session(self._get_engine()) as session:
            # Try to load existing
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == context.user_id,
            )
            existing = session.exec(stmt).first()
            if existing:
                existing.updated_at = datetime.utcnow()
                session.add(existing)
            else:
                conversation = Conversation(
                    user_id=context.user_id,
                )
                session.add(conversation)
            session.commit()

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        with Session(self._get_engine()) as session:
            stmt = select(Conversation).where(
                Conversation.user_id == context.user_id,
            )

            if after:
                cursor_stmt = select(Conversation.created_at).where(
                    Conversation.id == int(after)
                )
                cursor_time = session.exec(cursor_stmt).first()
                if cursor_time:
                    if order == "asc":
                        stmt = stmt.where(Conversation.created_at > cursor_time)
                    else:
                        stmt = stmt.where(Conversation.created_at < cursor_time)

            if order == "asc":
                stmt = stmt.order_by(Conversation.created_at.asc())
            else:
                stmt = stmt.order_by(Conversation.created_at.desc())

            stmt = stmt.limit(limit + 1)
            results = session.exec(stmt).all()

            has_more = len(results) > limit
            data = results[:limit]

            return Page(
                data=[conversation_to_thread_metadata(c) for c in data],
                has_more=has_more,
                after=str(data[-1].id) if data else None,
            )

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == context.user_id,
            )
            conversation = session.exec(stmt).first()
            if conversation:
                session.delete(conversation)
                session.commit()

    # -- Thread Item operations ---------------------------------------------

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            stmt = select(Message).where(
                Message.conversation_id == conversation_id,
                Message.user_id == context.user_id,
            )

            # Handle pagination cursor (skip sentinel values like '__fake_id__')
            if after and after.isdigit():
                cursor_stmt = select(Message.created_at).where(
                    Message.id == int(after)
                )
                cursor_time = session.exec(cursor_stmt).first()
                if cursor_time:
                    if order == "asc":
                        stmt = stmt.where(Message.created_at > cursor_time)
                    else:
                        stmt = stmt.where(Message.created_at < cursor_time)

            if order == "asc":
                stmt = stmt.order_by(Message.created_at.asc())
            else:
                stmt = stmt.order_by(Message.created_at.desc())

            stmt = stmt.limit(limit + 1)
            messages = session.exec(stmt).all()

            has_more = len(messages) > limit
            data = messages[:limit]

            items = [deserialize_thread_item(msg) for msg in data]

            # Log loaded items (CR-101)
            logger.info(f"[STORE] Loaded {len(items)} items from thread {thread_id}")
            for item in items:
                logger.info(f"[STORE]   - id={item.id}, type={item.type}")

            return Page(
                data=items,
                has_more=has_more,
                after=str(data[-1].id) if data else None,
            )

    async def add_thread_item(self, thread_id: str, item, context: RequestContext) -> None:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)

        # Log incoming item (CR-101) - safely handle items without id attribute
        item_id = getattr(item, "id", "no-id")
        item_type = getattr(item, "type", "unknown")

        # Generate unique ID for assistant messages with placeholder IDs
        if item_type == "assistant_message":
            if item_id in ("__fake_id__", "no-id", "") or item_id.startswith("__"):
                # Create ThreadMetadata for generate_item_id
                thread_meta = ThreadMetadata(
                    id=thread_id,
                    created_at=datetime.now(timezone.utc)
                )
                # Generate unique ID
                unique_id = self.generate_item_id("message", thread_meta, context)
                # Update the item's ID
                item.id = unique_id
                item_id = unique_id
                logger.info(f"[STORE] Generated unique ID for assistant message: {unique_id}")

        logger.info(f"[STORE] Saving item: id={item_id}, type={item_type}, thread={thread_id}")

        with Session(self._get_engine()) as session:
            if item_type == "user_message":
                role = MessageRole.USER
            else:
                role = MessageRole.ASSISTANT

            message = Message(
                conversation_id=conversation_id,
                user_id=context.user_id,
                role=role,
                content=json.dumps(serialize_thread_item(item)),
                created_at=datetime.utcnow(),
            )
            session.add(message)
            session.commit()
            session.refresh(message)

            # Log saved message (CR-101)
            logger.info(f"[STORE] Saved to DB: message.id={message.id}, item.id={item_id}")

    async def save_item(self, thread_id: str, item, context: RequestContext) -> None:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            # Try to find by item.id if it looks like an int
            try:
                item_id_int = int(item.id)
                existing = session.get(Message, item_id_int)
                if existing and existing.conversation_id == conversation_id:
                    existing.content = json.dumps(serialize_thread_item(item))
                    session.add(existing)
                    session.commit()
                    return
            except (ValueError, TypeError):
                pass

            # If not found, add as new
            await self.add_thread_item(thread_id, item, context)

    async def load_item(self, thread_id: str, item_id: str, context: RequestContext):
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            stmt = select(Message).where(
                Message.id == int(item_id),
                Message.conversation_id == conversation_id,
            )
            message = session.exec(stmt).first()
            if not message:
                raise NotFoundError(f"Item {item_id} not found")
            return deserialize_thread_item(message)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        conversation_id = self._parse_thread_id(thread_id, context.user_id)
        with Session(self._get_engine()) as session:
            stmt = select(Message).where(
                Message.id == int(item_id),
                Message.conversation_id == conversation_id,
            )
            message = session.exec(stmt).first()
            if message:
                session.delete(message)
                session.commit()

    # -- Attachment operations (stubs - not needed for Phase III) -----------

    async def save_attachment(self, attachment, context: RequestContext) -> None:
        pass  # No-op for Phase III

    async def load_attachment(self, attachment_id: str, context: RequestContext):
        raise NotFoundError("Attachments not supported in Phase III")

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        pass  # No-op for Phase III

    # -- ID generation ------------------------------------------------------

    def generate_item_id(
        self,
        item_type: Literal[
            "thread", "message", "tool_call", "task",
            "workflow", "attachment", "sdk_hidden_context"
        ],
        thread: ThreadMetadata,
        context: RequestContext,
    ) -> str:
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    def generate_thread_id(self, context: RequestContext) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"

    # -- Internal helpers ---------------------------------------------------

    def _get_engine(self):
        """Get the SQLModel engine."""
        from src.database.session import engine
        return engine

    def _parse_thread_id(self, thread_id: str, user_id: str) -> int:
        """
        Parse ChatKit thread ID to database Conversation ID.

        Handles three cases:
        1. Numeric string (existing conversation): "123" → 123
        2. User ID or ChatKit-generated ID: find existing conversation for user
        3. No existing conversation: create new one

        Returns: Integer conversation ID
        """
        # Case 1: Try numeric conversion (existing conversation by ID)
        try:
            return int(thread_id)
        except ValueError:
            pass

        # Case 2 & 3: Non-numeric ID (user_id or ChatKit-generated)
        # Find most recent conversation for this user, or create new one
        with Session(self._get_engine()) as session:
            stmt = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.created_at.desc()).limit(1)

            existing = session.exec(stmt).first()
            if existing:
                logger.info(f"Mapped thread_id '{thread_id}' to existing conversation {existing.id}")
                return existing.id

            # Create new conversation
            new_conv = Conversation(user_id=user_id)
            session.add(new_conv)
            session.commit()
            session.refresh(new_conv)
            logger.info(f"Created new conversation {new_conv.id} for thread_id '{thread_id}'")
            return new_conv.id
