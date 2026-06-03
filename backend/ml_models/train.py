import os
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from django.conf import settings


def train(features_matrix):
    model = IsolationForest(
        n_estimators=50,
        max_samples='auto',
        contamination=0.15,
        random_state=42,
        n_jobs=1,
    )
    X = np.array(features_matrix).astype(np.float32)
    model.fit(X)

    path = os.path.join(settings.BASE_DIR, 'ml_models', 'anomaly_model.pkl')
    with open(path, 'wb') as f:
        pickle.dump(model, f)

    return path
