"use client";

import { useState, useCallback } from "react";
import { chatApi, type ToolCallInfo } from "@/lib/chat-api";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCallInfo[];
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: number | null;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(userId: string): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      setIsLoading(true);
      setError(null);

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        // Call the chat API
        const response = await chatApi.sendMessage(
          userId,
          text,
          conversationId
        );

        // Update conversation ID if this is the first message
        if (!conversationId && response.conversation_id) {
          setConversationId(response.conversation_id);
        }

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
          toolCalls: response.tool_calls.length > 0 ? response.tool_calls : undefined,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        // Add error message to chat
        const errorChatMessage: ChatMessage = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `Error: ${errorMessage}`,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorChatMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, conversationId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearMessages,
  };
}
