import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {}, // ✅ DISABLE turbopack safely

  async rewrites() {
    // Auth is now handled by Better Auth in Next.js (app/api/auth/[...all]/route.ts)
    // Only proxy non-auth API requests to FastAPI backend
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
    ];
  },

  webpack: (config) => {
    config.resolve.alias["@"] = path.resolve(__dirname);
    return config;
  },
};

export default nextConfig;
