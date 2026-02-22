# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build arguments - these are only used during build
# DATABASE_URL: Required by auth-server.ts during build (can be dummy value)
# NEON_DATABASE_URL: Optional Neon serverless database URL
# NEXT_PUBLIC_API_URL: This value gets BAKED INTO the image (important!)
ARG DATABASE_URL="postgresql://localhost/dummy"
ARG NEON_DATABASE_URL=""
ARG NEXT_PUBLIC_API_URL="http://localhost:3000"

# Export build arguments as environment variables for Next.js build
ENV DATABASE_URL=${DATABASE_URL}
ENV NEON_DATABASE_URL=${NEON_DATABASE_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy package files from builder
COPY --from=builder /app/package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

# Expose port
EXPOSE 3000

# Runtime environment variables (can be overridden by container)
ENV NODE_ENV=production

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start Next.js application
CMD ["npm", "start"]
