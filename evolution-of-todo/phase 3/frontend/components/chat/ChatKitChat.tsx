"use client";

import { useChatKit, ChatKit } from "@openai/chatkit-react";

interface ChatKitChatProps {
  userId: string;
}

export function ChatKitChat({ userId }: ChatKitChatProps) {
  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: "local-dev",
      fetch: async (url, init) => {
        const headers = new Headers(init?.headers);
        headers.set("X-User-Id", userId);

        return fetch(url, {
          ...init,
          headers,
          credentials: "include",
        });
      },
    },
    initialThread: userId,
    composer: {
      placeholder: "Ask me about your tasks...",
    },
    header: {
      title: {
        text: "AI Todo Assistant",
      },
    },
    theme: "light",
  });

  return (
    <div className="h-[calc(100vh-12rem)] w-full rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
      <ChatKit control={chatkit.control} style={{ height: "100%", width: "100%" }} />
    </div>
  );
}
