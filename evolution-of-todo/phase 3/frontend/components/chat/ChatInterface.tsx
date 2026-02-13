"use client";

import { useState, useRef, useEffect } from "react";
import { useChat, type ChatMessage } from "@/hooks/useChat";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { cn } from "@/lib/utils";

interface ChatInterfaceProps {
  userId: string;
}

export function ChatInterface({ userId }: ChatInterfaceProps) {
  const { messages, isLoading, sendMessage } = useChat(userId);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue;
    setInputValue("");
    await sendMessage(message);

    // Focus back on input
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const examplePrompts = [
    "Show me all my tasks",
    "Create a task to buy groceries",
    "Mark my first task as complete",
    "What tasks do I have for today?",
  ];

  const handleExampleClick = (prompt: string) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="max-w-md space-y-4">
              <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                AI Todo Assistant
              </h2>
              <p className="text-zinc-600 dark:text-zinc-400">
                Ask me anything about your tasks. I can help you create, update, and manage your todos.
              </p>
              <div className="space-y-2">
                <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Try these examples:
                </p>
                <div className="grid gap-2">
                  {examplePrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handleExampleClick(prompt)}
                      className="px-4 py-2 text-sm text-left text-zinc-700 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded-lg transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center">
                  <Spinner size="sm" />
                </div>
                <div className="flex-1">
                  <div className="inline-block px-4 py-2 rounded-lg bg-zinc-100 dark:bg-zinc-800">
                    <Spinner size="sm" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-zinc-200 dark:border-zinc-800 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            disabled={isLoading}
            rows={1}
            className="flex-1 px-4 py-2 text-sm bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 resize-none disabled:opacity-50 disabled:cursor-not-allowed text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-500 dark:placeholder:text-zinc-400"
            style={{ minHeight: "40px", maxHeight: "120px" }}
          />
          <Button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            variant="primary"
            className="self-end"
          >
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex items-start gap-3",
        isUser && "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300"
        )}
      >
        {isUser ? "U" : "AI"}
      </div>

      {/* Message Content */}
      <div className={cn("flex-1 max-w-[80%]", isUser && "flex justify-end")}>
        <div
          className={cn(
            "inline-block px-4 py-2 rounded-lg",
            isUser
              ? "bg-blue-600 text-white"
              : "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
          )}
        >
          <p className="text-sm whitespace-pre-wrap break-words">
            {message.content}
          </p>

          {/* Tool Calls Display */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className="mt-2 pt-2 border-t border-zinc-200 dark:border-zinc-700 space-y-1">
              <p className="text-xs font-medium opacity-75">Actions taken:</p>
              {message.toolCalls.map((toolCall, index) => (
                <div
                  key={index}
                  className="text-xs opacity-75 bg-zinc-200 dark:bg-zinc-700 px-2 py-1 rounded"
                >
                  {toolCall.tool}
                </div>
              ))}
            </div>
          )}

          <p className="text-xs opacity-75 mt-1">
            {message.timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
