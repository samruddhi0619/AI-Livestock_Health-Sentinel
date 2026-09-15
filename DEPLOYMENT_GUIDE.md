# AI-Livestock Health Sentinel Deployment Guide

This guide covers deployment instructions for **AI-Livestock Health Sentinel** across three recommended production environments:

---

## Option 1: Free Cloud Hosting (Render + Vercel + MongoDB Atlas) — Recommended for Demos & SIH

This is the fastest, free-tier cloud deployment path requiring 0 server maintenance.

```
+---------------------------------------------------------------------------------------------------+
|                        Cloud PaaS Architecture (Free Tier Ready)                                  |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ Vercel / Netlify ]  ──► Hosts React Frontend (CDN, Global SSL, Auto Git Deploys)               |
|            │                                                                                      |
|            ▼ (API Proxy / CORS)                                                                   |
|  [ Render / Railway ]  ──► Hosts FastAPI Backend (Python 3.11, Uvicorn, PyTorch, DBSCAN)            |
|            │                                                                                      |
|            ▼                                                                                      |
|  [ MongoDB Atlas ]     ──► Cloud Managed Database (512MB Free M0 Cluster)                        |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

### Step 1: Deploy Database on MongoDB Atlas
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Build a **Free M0 Shared Cluster** (e.g. AWS / Mumbai Region `ap-south-1`).
3. Under **Database Access**, create a database user (e.g. `sentinel_user` with password `SecurePassword123`).
4. Under **Network Access**, click **Add IP Address** and select **Allow Access from Anywhere (`0.0.0.0/0`)**.
5. Copy your connection string:
   `mongodb+srv://sentinel_user:SecurePassword123@cluster0.mongodb.net/ai_livestock_sentinel?retryWrites=true&w=majority`

---

### Step 2: Deploy FastAPI Backend on Render / Railway
1. Sign in to [Render](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository containing the `backend/` directory.
4. Set configuration:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `MONGODB_URI` = `<Your MongoDB Atlas Connection String>`
   - `MONGODB_DB_NAME` = `ai_livestock_sentinel`
   - `JWT_SECRET` = `sih_2026_sentinel_super_secret_key_90123`
   - `CORS_ORIGINS` = `*`
6. Click **Create Web Service**. Once deployed, copy your backend URL (e.g., `https://ai-livestock-sentinel-backend.onrender.com`).
7. Seed initial demonstration data by triggering `POST https://ai-livestock-sentinel-backend.onrender.com/api/admin/seed-demo-data`.

---

### Step 3: Deploy React Frontend on Vercel
1. Sign in to [Vercel](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Set Framework Preset: **Vite**.
5. Set Root Directory: `frontend`.
6. Update `frontend/vercel.json` with your Render backend URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://ai-livestock-sentinel-backend.onrender.com/api/:path*"
       },
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```
7. Click **Deploy**. Vercel will build and publish your app with free HTTPS (e.g. `https://ai-livestock-sentinel.vercel.app`).

---

## Option 2: 1-Command Docker Compose Deployment (Local or Cloud VPS)

Ideal for DigitalOcean, AWS EC2, GCP, Azure VM, or local server installations.

### Prerequisites
- Docker Engine & Docker Compose installed.

### Execution
1. Clone the repository to your host server:
   ```bash
   git clone https://github.com/your-org/ai-livestock-health-sentinel.git
   cd ai-livestock-health-sentinel
   ```

2. Start all 3 containers (**MongoDB**, **FastAPI Backend**, **Nginx React Frontend**):
   ```bash
   docker-compose up -d --build
   ```

3. Verify running containers:
   ```bash
   docker-compose ps
   ```

4. Access services:
   - **Frontend UI**: `http://<SERVER_IP>:80`
   - **Backend API**: `http://<SERVER_IP>:8000/docs`
   - **MongoDB**: `localhost:27017`

5. Seed SIH demonstration dataset inside container:
   ```bash
   docker exec -it sentinel_backend python generate_demo_data.py
   ```

---

## Option 3: Production VPS with Nginx & Certbot SSL

For institutional government deployment on an Ubuntu 22.04 LTS server with domain name and HTTPS certificate.

1. **System Setup**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git
   ```

2. **Backend Systemd Service (`/etc/systemd/system/sentinel-backend.service`)**:
   ```ini
   [Unit]
   Description=AI-Livestock Sentinel FastAPI Backend
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/var/www/ai-livestock-sentinel/backend
   ExecStart=/var/www/ai-livestock-sentinel/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Nginx Reverse Proxy Config (`/etc/nginx/sites-available/sentinel`)**:
   ```nginx
   server {
       server_name sentinel.yourdomain.gov.in;

       location / {
           root /var/www/ai-livestock-sentinel/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **SSL Certificate Activation**:
   ```bash
   sudo certbot --nginx -d sentinel.yourdomain.gov.in
   ```

---

## Verification & Health Check Endpoints

| Service | Endpoint | Success Response |
| :--- | :--- | :--- |
| **API Health** | `GET /api/health` | `{"status": "online", "database": "connected"}` |
| **OpenAPI Docs** | `GET /docs` | Swagger UI Console |
| **Alerts Seeder** | `POST /api/alerts/seed-samples` | `{"status": "success"}` |
| **SIH Demo Dataset** | `POST /api/admin/seed-demo-data` | `{"status": "success", "scenario": "Wagholi Cluster"}` |
