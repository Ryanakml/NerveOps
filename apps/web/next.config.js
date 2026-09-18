/** @type {import('next').NextConfig} */
const nextConfig = {
  // M0-01 shell: standalone output keeps future Docker/Compose (#3) simple.
  output: "standalone",
  poweredByHeader: false
};

module.exports = nextConfig;
