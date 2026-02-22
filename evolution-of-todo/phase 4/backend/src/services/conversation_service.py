"""
Conversation Service - Manages conversation state, message history, and context assembly.

This service provides stateless operations for conversation lifecycle management:
- Creating and retrieving conversations
- Fetching message history
- Storing user and assistant messages atomically
- Building context arrays for agent consumption
"""

from sqlmodel import Session, select
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from typing import Optional


class ConversationService:
    """
    Stateless service for managing conversation state and message history.

    All operations enforce user isolation and maintain data consistency.
    Source of truth is the database; no server-side session state is maintained.
    """

    def __init__(self, db: Session):
        """
        Initialize the conversation service.

        Args:
            db: SQLModel database session for all operations
        """
        self.db = db

    def create_or_get_conversation(
        self,
        user_id: str,
        conversation_id: Optional[int] = None
    ) -> Conversation:
        """
        Create a new conversation or retrieve an existing one.

        This is an idempotent operation that either:
        - Fetches an existing conversation (if conversation_id provided)
        - Creates a new conversation (if conversation_id is None)

        Args:
            user_id: The ID of the user owning the conversation
            conversation_id: Optional conversation ID to retrieve

        Returns:
            Conversation object (either fetched or newly created)

        Raises:
            ValueError: If conversation_id provided but not found or user_id mismatch
        """
        if conversation_id is not None:
            # Fetch existing conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = self.db.exec(statement).first()

            if conversation is None:
                raise ValueError(
                    f"Conversation {conversation_id} not found or unauthorized for user {user_id}"
                )

            return conversation
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation

    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: str,
        limit: int = 100
    ) -> list[Message]:
        """
        Retrieve message history for a conversation.

        Messages are returned in chronological order (oldest first) to maintain
        conversation flow when building context arrays.

        Args:
            conversation_id: The conversation ID to fetch messages from
            user_id: The user ID for authorization check
            limit: Maximum number of messages to retrieve (default: 100)

        Returns:
            List of Message objects ordered by creation time (ascending)
        """
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        messages = self.db.exec(statement).all()
        return list(messages)

    def store_messages(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        assistant_message: str
    ) -> tuple[Message, Message]:
        """
        Store user and assistant messages atomically.

        Both messages are committed together to ensure conversation consistency.
        If any error occurs, both messages are rolled back.

        Args:
            conversation_id: The conversation these messages belong to
            user_id: The user ID for both messages
            user_message: The user's message content
            assistant_message: The assistant's response content

        Returns:
            Tuple of (user_message_object, assistant_message_object)

        Raises:
            Exception: Any database error during commit (after rollback)
        """
        try:
            # Create user message
            user_msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=MessageRole.USER,
                content=user_message
            )

            # Create assistant message
            assistant_msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=assistant_message
            )

            # Add both messages
            self.db.add(user_msg)
            self.db.add(assistant_msg)

            # Commit atomically
            self.db.commit()

            # Refresh to get generated IDs and timestamps
            self.db.refresh(user_msg)
            self.db.refresh(assistant_msg)

            return (user_msg, assistant_msg)

        except Exception as e:
            # Rollback on any error
            self.db.rollback()
            raise e

    def build_context_array(
        self,
        conversation_id: int,
        user_id: str,
        new_message: str
    ) -> list[dict]:
        """
        Build a context array for agent consumption.

        Fetches conversation history and formats it as a list of role/content dicts,
        then appends the new user message. This array is ready to be sent to the
        agent/LLM API.

        Args:
            conversation_id: The conversation to build context from
            user_id: The user ID for authorization
            new_message: The new user message to append

        Returns:
            List of dicts with "role" and "content" keys, ordered chronologically
            Example: [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
        """
        # Fetch existing history
        history = self.get_conversation_history(conversation_id, user_id)

        # Convert to context array format
        context_array = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in history
        ]

        # Append new user message
        context_array.append({
            "role": "user",
            "content": new_message
        })

        return context_array
