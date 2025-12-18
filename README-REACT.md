# React frontend + Express backend (scaffold)

This repository now contains a minimal React frontend (Vite) in `frontend/` and a simple Express backend in `backend/` that can serve the built frontend and the `data/` folder with assets.

Quick dev steps

1. Frontend dev (run from project root):

```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

2. Build frontend and run backend:

```bash
cd frontend
npm install
npm run build
cd ../backend
npm install
npm start
# open http://localhost:5000
```

Notes
- The React app references images under `/data/raw/...` which the backend serves from the repository `data/` folder. When developing with `vite` from `frontend/`, you may need to copy assets into `frontend/public/` or adjust paths. The backend server will serve assets correctly when running the built frontend (production flow above).
- Tailwind is included via CDN in the Vite `index.html` to preserve the original layout quickly.
