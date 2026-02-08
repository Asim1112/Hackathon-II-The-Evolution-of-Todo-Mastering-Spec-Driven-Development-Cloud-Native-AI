import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {}, // ✅ DISABLE turbopack safely

  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "https://asim1112-hackathon2.hf.space";
    return [
      {
        source: "/api/auth/:path*",
        destination: `${backendUrl}/api/auth/:path*`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },

  webpack: (config) => {
    config.resolve.alias["@"] = path.resolve(__dirname);
    return config;
  },
};

export default nextConfig;
