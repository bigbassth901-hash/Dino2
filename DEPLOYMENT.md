# Deployment Guide

Production deployment guide for the Film Asset Management system.

## Deployment Checklist

Before deploying to production:

- [ ] All tests pass
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Security hardening completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] SSL/HTTPS enabled
- [ ] Rate limiting implemented
- [ ] Authentication added (if required)

## Environment Setup

### Production Environment Variables

Create a `.env.production` file:

```env
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Backend
API_BASE_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional
MAX_UPLOAD_SIZE=100MB
ALLOWED_VIDEO_FORMATS=mp4,mov,avi
```

## Backend Deployment Options

### Option 1: Docker (Recommended)

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads keyframes training_data chroma_db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/keyframes:/app/keyframes
      - ./backend/training_data:/app/training_data
      - ./backend/chroma_db:/app/chroma_db
    env_file:
      - .env
    restart: unless-stopped

  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Cloud Platforms

#### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy backend
cd backend
railway login
railway init
railway up
```

#### Render
1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `cd backend && pip install -r requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

#### AWS EC2
```bash
# SSH into instance
ssh ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone repository
git clone your-repo.git
cd your-repo/backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/film-asset-api.service
```

Systemd service file:
```ini
[Unit]
Description=Film Asset Management API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo/backend
Environment="PATH=/home/ubuntu/your-repo/backend/venv/bin"
ExecStart=/home/ubuntu/your-repo/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable film-asset-api
sudo systemctl start film-asset-api
```

## Frontend Deployment Options

### Option 1: Static Hosting (Vercel, Netlify)

Build for production:
```bash
npm run build
```

Deploy to Vercel:
```bash
npm i -g vercel
vercel --prod
```

Deploy to Netlify:
```bash
npm i -g netlify-cli
netlify deploy --prod --dir=dist
```

### Option 2: Docker with Nginx

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Database Setup

### Supabase Production

1. Upgrade to paid plan for production
2. Enable Point-in-Time Recovery
3. Set up daily backups
4. Configure connection pooling
5. Review and tighten RLS policies

### Security Hardening

Update RLS policies for production:

```sql
-- Remove public access policies
DROP POLICY IF EXISTS "Allow public read access to shots" ON shots;
DROP POLICY IF EXISTS "Allow public insert to shots" ON shots;

-- Add authenticated-only policies
CREATE POLICY "Users can read own shots"
  ON shots FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own shots"
  ON shots FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);
```

## Performance Optimization

### Backend Optimizations

1. **Use Gunicorn with multiple workers:**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Enable caching:**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

3. **Add request queuing:**
```python
from fastapi import BackgroundTasks

@app.post("/api/upload")
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video, file)
    return {"status": "processing"}
```

### Frontend Optimizations

1. **Enable compression:**
```javascript
// vite.config.ts
import viteCompression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [react(), viteCompression()],
});
```

2. **Lazy load components:**
```typescript
import { lazy, Suspense } from 'react';

const MainGallery = lazy(() => import('./components/MainGallery'));

<Suspense fallback={<Loading />}>
  <MainGallery />
</Suspense>
```

3. **Add CDN for static assets:**
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@dnd-kit/core'],
        },
      },
    },
  },
});
```

## SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring and Logging

### Application Monitoring

Use Sentry for error tracking:

```bash
npm install @sentry/react
```

```typescript
// main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
});
```

### Server Monitoring

Use PM2 for process management:

```bash
npm install -g pm2

# Start backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name film-api

# Monitor
pm2 monit

# Auto-restart on crashes
pm2 startup
pm2 save
```

### Log Aggregation

Use structured logging:

```python
import logging
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
```

## Backup Strategy

### Database Backups

```bash
# Supabase automatic backups (managed)
# Manual backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### File Storage Backups

```bash
# Backup uploaded files and keyframes
tar -czf backup_$(date +%Y%m%d).tar.gz backend/uploads backend/keyframes

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

## Health Checks

Add health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if storage_service.supabase else "disconnected",
        "timestamp": datetime.now().isoformat()
    }
```

Monitor with:
```bash
curl http://your-api.com/health
```

## Scaling Considerations

### Horizontal Scaling

1. Use load balancer (Nginx, HAProxy)
2. Deploy multiple backend instances
3. Share ChromaDB via network storage
4. Use Redis for session management

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Add GPU for faster ML inference
3. Use SSD for faster file I/O

## Security Best Practices

1. **API Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/upload")
@limiter.limit("5/minute")
async def upload_video():
    ...
```

2. **Input Validation:**
```python
from pydantic import validator

class UploadRequest(BaseModel):
    @validator('file')
    def validate_file_size(cls, v):
        if v.size > 100 * 1024 * 1024:  # 100MB
            raise ValueError('File too large')
        return v
```

3. **CORS Restrictions:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Post-Deployment

1. Run smoke tests
2. Monitor error rates
3. Check performance metrics
4. Verify backups are working
5. Test disaster recovery procedures

## Rollback Plan

If deployment fails:

```bash
# Docker rollback
docker-compose down
docker-compose up -d --build

# Git rollback
git revert HEAD
git push

# Database rollback
psql $DATABASE_URL < backup_20240101.sql
```

## Support and Maintenance

Schedule regular maintenance:
- Weekly: Review logs, check backups
- Monthly: Update dependencies, security patches
- Quarterly: Performance audit, cost optimization
