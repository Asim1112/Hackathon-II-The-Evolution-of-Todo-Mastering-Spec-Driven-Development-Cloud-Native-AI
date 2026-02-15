"use client";

import { useAuth } from "@/hooks/useAuth";
import { ChatKitChat } from "@/components/chat/ChatKitChat";
import { LoadingScreen } from "@/components/ui/Spinner";

export default function ChatPage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="Loading chat..." />;
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-zinc-600 dark:text-zinc-400">
          Please sign in to use the chat.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
          AI Chat Assistant
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 mt-1">
          Chat with your AI assistant to manage your tasks
        </p>
      </div>

      <ChatKitChat userId={user.userId} />
    </div>
  );
}
