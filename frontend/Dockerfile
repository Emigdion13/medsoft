# Build stage - Install dependencies and build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy all files (excluding those in .dockerignore)
COPY . .

# Install all dependencies (including dev for building)
RUN npm ci

# Set environment variables
ENV VITE_API_URL=http://backend:8000/api

# Build the application
RUN npm run build

# Production stage - Serve with Nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
