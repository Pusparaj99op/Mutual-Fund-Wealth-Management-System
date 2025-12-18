"""FastAPI scaffold for Raptor prototype."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from raptor.src import data_loader, preprocessing, monte_carlo, black_scholes, models
import logging

logger = logging.getLogger('raptor.api')
app = FastAPI(title='Raptor Prototype API')

# Allow CORS for local dev (prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    scheme_code: str
    horizon: int = 30
    n_sim: int = 500
    include_samples: bool = False
    samples_to_return: int = 50


@app.get('/')
def root():
    return {'status': 'ok', 'service': 'raptor'}


@app.post('/predict')
def predict(req: PredictRequest):
    try:
        df = data_loader.load_nav_timeseries(req.scheme_code)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    sims = monte_carlo.monte_carlo_forecast(df['nav'], n_sim=req.n_sim, horizon=req.horizon)
    expected, var = black_scholes.black_scholes_gbm_forecast(df['nav'], horizon=req.horizon)
    # compute percentile bands for Monte Carlo (10th, 50th, 90th)
    import numpy as np
    p10 = np.percentile(sims, 10, axis=0).tolist()
    p50 = np.percentile(sims, 50, axis=0).tolist()
    p90 = np.percentile(sims, 90, axis=0).tolist()
    samples = None
    if req.include_samples and req.samples_to_return>0:
        k = min(req.samples_to_return, sims.shape[0])
        rs = np.random.RandomState(0)
        idx = rs.choice(sims.shape[0], size=k, replace=False)
        samples = sims[idx].tolist()
    return {
        'scheme_code': req.scheme_code,
        'monte_carlo': {
            'simulations_shape': sims.shape,
            'percentile_10': p10,
            'percentile_50': p50,
            'percentile_90': p90
        },
        'gbm_expected': expected.tolist(),
        'samples': samples
    }


@app.get('/schemes')
def schemes():
    return {'schemes': data_loader.list_available_schemes()[:200]}


class RecommendRequest(BaseModel):
    scheme_codes: Optional[List[str]] = None
    amount: float = 10000.0
    top_k: int = 5
    risk_aversion: float = 3.0
    min_obs: int = 100


@app.post('/recommend')
def recommend(req: RecommendRequest):
    try:
        from raptor.src import recommender
        out = recommender.recommend_black_litterman(scheme_codes=req.scheme_codes,
                                                   amount=req.amount,
                                                   top_k=req.top_k,
                                                   risk_aversion=req.risk_aversion,
                                                   min_obs=req.min_obs)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TrainRequest(BaseModel):
    horizon: int = 7
    n_estimators: int = 100
    sample_limit: Optional[int] = None


@app.post('/train_pooled')
def train_pooled(req: TrainRequest):
    try:
        from raptor.src import train_baselines
        res = train_baselines.train_pooled_rf(horizon=req.horizon, n_estimators=req.n_estimators, sample_limit=req.sample_limit)
        return res
    except ModuleNotFoundError as e:
        raise HTTPException(status_code=501, detail='Required ML dependencies missing: '+str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PredictModelRequest(BaseModel):
    scheme_code: str
    horizon: int = 7


@app.post('/predict_model')
def predict_model(req: PredictModelRequest):
    # Prepare latest feature row for scheme
    try:
        from raptor.src import models as rmodels
        from raptor.src import preprocessing
        feat_file = preprocessing.FEATURES_DIR / f'features_{req.scheme_code}.parquet'
        if not feat_file.exists():
            raise HTTPException(status_code=404, detail='Features for scheme not found; run feature generation')
        fg = pd.read_parquet(feat_file)
        last = fg.sort_values('date').iloc[-1]
        # feature names expected by pooled model
        artifact = rmodels.load_pooled_model()
        feat_cols = artifact['feat_cols']
        feature_row = {c: float(last.get(c, 0.0)) for c in feat_cols if c != 'scheme_code_cat'}
        pred = rmodels.predict_pooled_one(req.scheme_code, feature_row)
        return {'scheme_code': req.scheme_code, 'pred_target_ret': pred}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModuleNotFoundError as e:
        raise HTTPException(status_code=501, detail='Required ML libs missing: '+str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/backtest')
def backtest_endpoint(lookback_days: int = 252, rebalance_freq_days: int = 21, top_k: int = 5):
    try:
        from raptor.src import backtest
        out = backtest.backtest_black_litterman(lookback_days=lookback_days, rebalance_freq_days=rebalance_freq_days, top_k=top_k)
        # serialize portfolio_nav (pandas Series) to list of {date, nav}
        ser = out['portfolio_nav']
        series_list = [{'date': str(d.date()), 'nav': float(v)} for d, v in zip(ser.index, ser.values)]
        metrics = out['metrics']
        return {'series': series_list, 'metrics': metrics, 'periods': [(str(s[0].date()), str(s[1].date())) for s in out.get('periods', [])]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
