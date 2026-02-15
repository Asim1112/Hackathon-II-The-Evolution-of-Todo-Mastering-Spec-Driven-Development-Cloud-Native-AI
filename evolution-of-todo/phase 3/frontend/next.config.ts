import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {}, // ✅ DISABLE turbopack safely

  async rewrites() {
    // Auth is now handled by Better Auth in Next.js (app/api/auth/[...all]/route.ts)
    // Only proxy non-auth API requests to FastAPI backend
    const backendUrl = process.env.BACKEND_API_URL || 'https://asim1112-todo-ai-chatbot.hf.space';
    return [
      {
        source: "/api/:userId/chat",
        destination: `${backendUrl}/api/:userId/chat`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: "/chatkit",
        destination: `${backendUrl}/chatkit`,
      },
    ];
  },

  webpack: (config) => {
    config.resolve.alias["@"] = path.resolve(__dirname);
    return config;
  },
};

export default nextConfig;
