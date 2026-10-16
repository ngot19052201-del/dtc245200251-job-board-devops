FROM node:20-alpine

# Set working directory
WORKDIR /usr/src/app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy package definitions
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production || npm install --only=production

# Copy application source code
COPY . .

# Ensure uploads directory exists and has proper permissions
RUN mkdir -p public/uploads/cvs && chown -R node:node /usr/src/app

# Switch to non-root user
USER node

# Expose container port
EXPOSE 3000

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start application using dumb-init
CMD ["dumb-init", "node", "server.js"]
