from raptor.src import preprocessing
import pandas as pd


def test_clean_and_features():
    # create small sample
    df = pd.DataFrame({'date': pd.date_range('2020-01-01', periods=5), 'nav': [10,11,10.5,10.8,11.0]})
    c = preprocessing.clean_nav_df(df)
    assert 'nav' in c.columns
    fg = preprocessing.make_rolling_features(c)
    assert any(col.startswith('roll_mean_') for col in fg.columns)
