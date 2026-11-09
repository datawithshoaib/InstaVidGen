import type { NextConfig } from "next";

// The browser talks only to Next.js; API and media requests are proxied to FastAPI.
const backendUrl = (process.env.BACKEND_URL ?? "http://localhost:8002").replace(/\/$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/media/:path*", destination: `${backendUrl}/media/:path*` },
    ];
  },
  experimental: {
    // AI generation and video rendering can take longer than the 30s default.
    proxyTimeout: 120_000,
  },
};

export default nextConfig;
