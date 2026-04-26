# Build stage - Install dependencies and build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy all files (excluding those in .dockerignore)
COPY . .

# Install all dependencies (including dev for building)
RUN npm ci

# Set environment variables for production build
# In Docker, the frontend serves from same origin, so API path is relative
ENV VITE_API_URL=/api

# Build the application
RUN npm run build

# Production stage - Serve with Nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Remove default nginx config to avoid conflicts
RUN rm -f /etc/nginx/conf.d/default.conf || true

# Copy custom nginx configuration (with api proxy to backend)
COPY nginx.conf /etc/nginx/conf.d/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
