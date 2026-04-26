#!/bin/sh

# Start Vite dev server in background
npm run dev -- --host 0.0.0.0 --port 5173 &

# Wait for Vite to start
sleep 3

# Nginx config to proxy /api to backend and serve static files
cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Start nginx in foreground
nginx -g 'daemon off;'
