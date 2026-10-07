# Railway Deployment Guide (Zero-Downtime, Persistent URL)

This project is configured for continuous deployment on Railway connected to GitHub (`https://github.com/thedreamer975/SDE-BNB`).

> **Guarantee:** Because deployment is driven directly by GitHub webhook integration on Railway:
> 1. Any subsequent `git push origin main` will **automatically trigger a rebuild and redeployment**.
> 2. The **public accessible URL never changes** across redeployments and updates.

---

## 1. Deploying on Railway (Step-by-Step)

### A. Deploy Backend Service
1. Log in to [Railway](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select `thedreamer975/SDE-BNB`.
4. Click on the created service card → **Settings**:
   - **Root Directory**: `backend`
   - **Build Command**: (Automatically uses `Dockerfile` or Nixpacks)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Go to **Variables** and add:
   - `ENV`: `production`
   - `JWT_SECRET`: `supersecretjwtkeyforairbnbcloneproductionmustbe32charsorlonger!` (or generate a random 32+ char secret)
   - `COOKIE_SECURE`: `True`
   - `DATABASE_URL`: `sqlite:///./app.db`
   - `FRONTEND_ORIGIN`: (Set to your Frontend Railway URL, e.g. `https://sde-bnb-web.up.railway.app`)
6. Go to **Networking** → Click **Generate Domain**.
   - Note down this URL (e.g. `https://sde-bnb-api.up.railway.app`).

### B. Deploy Frontend Service
1. In the same Railway project, click **+ New** → **GitHub Repo** → select `thedreamer975/SDE-BNB`.
2. Click on the new service card → **Settings**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npm start`
3. Go to **Variables** and add:
   - `API_ORIGIN`: The Backend URL generated above (e.g. `https://sde-bnb-api.up.railway.app`)
   - `NODE_ENV`: `production`
4. Go to **Networking** → Click **Generate Domain** (e.g. `https://sde-bnb-web.up.railway.app`).
5. Update `FRONTEND_ORIGIN` in the Backend service to match this URL.

---

## 2. Verification

Once deployed:
1. Open the frontend public link in your browser.
2. Sign up or log in with demo accounts (`guest@demo.com` / `Demo1234`).
3. Browse listings, search with dates, place reservations, view trips, and access the host dashboard.
4. Any git push will automatically deploy updates while keeping the same URL intact.
