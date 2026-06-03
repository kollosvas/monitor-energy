import os
import pickle
import numpy as np
from django.conf import settings

_model = None
_model_path = None


def get_model():
    global _model, _model_path
    current_path = os.path.join(settings.BASE_DIR, 'ml_models', 'anomaly_model.pkl')
    if _model is None or current_path != _model_path:
        if os.path.exists(current_path):
            with open(current_path, 'rb') as f:
                _model = pickle.load(f)
            _model_path = current_path
        else:
            _model = None
            _model_path = None
    return _model


def predict(features):
    model = get_model()
    if model is None:
        return None
    X = np.array([features]).astype(np.float32)
    score = model.score_samples(X)
    is_anomaly = model.predict(X)[0] == -1
    anomaly_score = float(max(0, min(1, 1 - (score[0] + 0.5))))
    return {
        'is_anomaly': bool(is_anomaly),
        'anomaly_score': round(anomaly_score, 4),
    }
