/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: "http://127.0.0.1:1201/:path*",
      },
    ]
  },
}

export default nextConfig
