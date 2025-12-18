# 🚀 STARTUP GUIDE - Federal Wealth Management System

## ⚡ 30-Second Quick Start (Windows)

```bash
cd palloti
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py --full
```

Then in a **new terminal**:
```bash
venv\Scripts\activate
streamlit run app/dashboard.py
```

**URLs:**
- 🌐 Dashboard: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs
- ✅ Health: http://localhost:8000/health

---

## 📋 Detailed Startup Instructions

### Method 1: Automated Setup (Recommended)

#### Windows
```cmd
quickstart.bat
```

#### Mac/Linux
```bash
chmod +x quickstart.sh
./quickstart.sh
```

---

### Method 2: Manual Step-by-Step

#### Step 1: Environment Setup
```bash
# Navigate to project
cd palloti

# Create virtual environment
python -m venv venv

# Activate (choose your OS)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Initialize & Run
```bash
# Full initialization (data + models + backend)
python main.py --full
```

**Wait for:**
- ✓ Dataset generation (150 funds)
- ✓ Data preprocessing
- ✓ Model training
- ✓ Backend startup on port 8000

#### Step 4: Start Dashboard (New Terminal)
```bash
# Activate venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

streamlit run app/dashboard.py
```

---

### Method 3: Separate Backend & Dashboard

#### Terminal 1: Backend
```bash
venv\Scripts\activate  # or source venv/bin/activate
python main.py --backend
```

#### Terminal 2: Dashboard
```bash
venv\Scripts\activate  # or source venv/bin/activate
streamlit run app/dashboard.py
```

---

## 🔍 Verify Everything Works

### ✅ Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### ✅ API Documentation
Open http://localhost:8000/docs in your browser

### ✅ Dashboard
Open http://localhost:8501 in your browser

---

## 🐛 Troubleshooting

### Issue: "Python not found"
**Solution:**
```bash
# Check Python is installed
python --version

# If not, download from python.org
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue: "pip install fails"
**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Try installing with constraints
pip install -r requirements.txt --no-cache-dir
```

### Issue: "Cannot connect to API"
**Solution:**
- Ensure Terminal 1 (backend) is running
- Check http://localhost:8000/health
- Verify port 8000 is free

### Issue: "Dashboard shows error"
**Solution:**
- Restart backend (Terminal 1)
- Refresh browser (Ctrl+R / Cmd+R)
- Check API is accessible from dashboard

---

## 📂 File Structure After Setup

```
palloti/
├── data/
│   ├── raw/
│   │   └── MF_India_AI.json        ✓ Generated
│   ├── processed/
│   │   ├── features_scaled.csv     ✓ Generated
│   │   ├── processed_funds.csv     ✓ Generated
│   │   └── targets.csv             ✓ Generated
│   └── generate_dataset.py
│
├── models/
│   ├── xgboost_returns.pkl         ✓ Trained
│   ├── prophet_nav_forecast.pkl    ✓ Trained
│   ├── feature_scaler.pkl          ✓ Created
│   └── categorical_encoder.pkl     ✓ Created
│
├── services/
│   ├── data_preprocessing.py       ✓ Ready
│   ├── model_trainer.py            ✓ Ready
│   └── recommendation_engine.py    ✓ Ready
│
├── api/
│   └── main.py                     ✓ Backend running
│
├── app/
│   └── dashboard.py                ✓ Dashboard running
│
├── configs/
│   └── config.py                   ✓ Configured
│
├── utils/
│   └── helpers.py                  ✓ Ready
│
├── main.py                         ✓ Entry point
├── requirements.txt                ✓ Installed
├── README.md                       📖 Documentation
├── API_REFERENCE.md               📖 API Docs
└── logs/
    └── app.log                     ✓ Created
```

---

## 🎯 First Time User Guide

### Step 1: Open Dashboard
```
http://localhost:8501
```

### Step 2: Navigate to "Get Recommendations"
- Enter investment amount: **₹100,000**
- Choose type: **SIP**
- Select tenure: **60 months**
- Keep category: **All**
- Set risk: **4**

### Step 3: Click "Get Recommendations"
- Wait for analysis (5-10 seconds)
- View top 5 funds
- Read explanations

### Step 4: Explore Other Tabs
- **Analytics**: Market trends
- **Fund Details**: Search any fund
- **Comparison**: Compare 2-5 funds

### Step 5: Test API (Optional)
```bash
curl -X POST http://localhost:8000/recommend_funds \
  -H "Content-Type: application/json" \
  -d '{
    "investment_amount": 100000,
    "investment_type": "sip",
    "tenure_months": 60
  }'
```

---

## ⏱️ Initialization Timeline

| Step | Duration | Details |
|------|----------|---------|
| 1. Venv Setup | ~30s | Virtual environment creation |
| 2. Dependencies | ~2-3m | Pip install packages |
| 3. Data Gen | ~10s | Generate 150 funds |
| 4. Preprocessing | ~15s | Feature engineering |
| 5. Model Training | ~1-2m | XGBoost + Prophet |
| 6. Backend Start | ~5s | FastAPI startup |
| **Total** | **~4-6m** | First-time complete setup |

---

## 🔧 Advanced Options

### Skip Model Training (Faster)
```bash
python main.py --backend
# Assumes models already exist
```

### Regenerate Dataset Only
```bash
python data/generate_dataset.py
```

### Retrain Models Only
```bash
python services/data_preprocessing.py
python services/model_trainer.py
```

### Use Different Config
Edit `configs/config.py` before running

---

## 📊 System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|------------|
| Python | 3.9 | 3.10+ |
| RAM | 4 GB | 8 GB |
| Disk | 500 MB | 1 GB |
| CPU | Dual-core | Quad-core |
| OS | Windows/Mac/Linux | Any |

---

## 🔐 Security Notes

### Development vs Production
- **Development** (current): Open API, no auth
- **Production**: Add authentication, HTTPS, rate limiting

### Files to Protect
- `.env` - Environment variables
- `models/` - Trained models
- `data/raw/` - Sensitive data

---

## 📞 Quick Support

### Check Logs
```bash
# Real-time logs while running
# See console output

# Or check log file
cat logs/app.log
```

### Restart Everything
```bash
# Kill all processes
# Windows: Task Manager
# Mac/Linux: Ctrl+C in terminals

# Start fresh
python main.py --full
```

### Reset Everything
```bash
# Delete old data
rm -rf data/processed models/

# Reinitialize
python main.py --init
```

---

## ✨ First Steps After Startup

### 1. Check Dashboard (http://localhost:8501)
- [ ] Page loads without errors
- [ ] Can input investment amount
- [ ] Can get recommendations
- [ ] Can view analytics

### 2. Test API (http://localhost:8000/docs)
- [ ] GET /health returns 200
- [ ] POST /recommend_funds works
- [ ] GET /funds/{id} returns data

### 3. Review Generated Files
- [ ] data/raw/MF_India_AI.json exists
- [ ] data/processed/ has CSV files
- [ ] models/ has pickle files

---

## 📈 Next Steps

1. **Customize Dataset** - Replace with real MF data
2. **Tweak Models** - Adjust hyperparameters in config.py
3. **Add Features** - Extend recommendation logic
4. **Deploy** - Use Docker or cloud platform
5. **Integrate** - Connect to portfolio management system

---

## 🎓 Learning Resources

### Understand the System
1. Read [README.md](README.md)
2. Explore [API_REFERENCE.md](API_REFERENCE.md)
3. Review code comments
4. Check docstrings

### Run Examples
1. Use API docs (/docs)
2. Try dashboard features
3. Examine config.py settings
4. Study model training code

---

## ✅ Checklist Before Demo

- [ ] Backend running (http://localhost:8000/health → 200)
- [ ] Dashboard running (http://localhost:8501)
- [ ] Dataset generated (150+ funds)
- [ ] Models trained
- [ ] API docs accessible (/docs)
- [ ] Dashboard responsive
- [ ] Recommendations generating
- [ ] Analytics displaying
- [ ] Fund comparison working
- [ ] No console errors

---

## 🎯 Key Metrics to Track

After running, you should see:

✓ **Data Generation**
- 150 mutual funds created
- Realistic data distribution

✓ **Preprocessing**
- 150+ features engineered
- Data scaled and encoded

✓ **Model Training**
- XGBoost R² score: 0.70+
- Prophet fitted successfully

✓ **API Startup**
- 6 endpoints available
- Health check returns 200

✓ **Dashboard**
- 4 tabs fully functional
- Interactive charts load
- Recommendations appear

---

## 🚀 Performance Tips

### Faster Startup
```bash
# Skip data regeneration
rm data/raw/MF_India_AI.json  # Keep existing
python main.py --backend      # Reuse processed data
```

### Better Performance
- Use SSD for faster I/O
- Increase RAM for large datasets
- Close other apps during training

---

**Ready to go! 🎉**

Run `python main.py --full` and enjoy!

---

*Last Updated: December 2024*  
*Version: 1.0.0*
