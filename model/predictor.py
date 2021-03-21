import os
import pickle
import io
import flask
import random
from detoxify import Detoxify
import numpy as np
import lime
import torch
import torch.nn.functional as F
from lime.lime_text import LimeTextExplainer
# import ssl


# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context


model_path = os.environ['MODEL_PATH']


# A singleton for holding the model. This simply loads the model and holds it.
# It has a predict function that does a prediction based on the model and the input data.

class ScoringService(object):
    model = None  # Where we keep the model when it's loaded

    @classmethod
    def get_model(cls):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if cls.model is None:
            cls.model = Detoxify('original')
            cls.model.model.eval()
        return cls.model

    @classmethod
    def predict(cls, x):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        clf = cls.get_model()
        return clf.predict(x)


# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    #health = ScoringService.get_model() is not None  # You can insert a health check here
    health = True

    status = 200 if health else 404
    return flask.Response(response='I am alive!\n', status=status, mimetype='application/json')


@app.route('/ishate', methods=['POST'])
def is_hate():
    """Do an inference on a single batch of data. In this sample server, we take data as CSV, convert
    it to a pandas data frame for internal use and then convert the predictions back to CSV (which really
    just means one prediction per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'text/plain':
        data = flask.request.data.decode('utf-8')
        data = io.StringIO(data)
        data.seek(0)
        data = data.read()
    else:
        return flask.Response(response='This predictor only supports text data', status=415, mimetype='application/json')

    print('Invoked with: {}'.format(data))

    # Do the prediction
    prediction = ScoringService.predict(data)
    print(prediction)
    return flask.Response(response=str(prediction['toxicity'] > 0.6), status=200, mimetype='application/json')

@app.route("/whyhate", methods=["POST"])
def why_hate():
    text = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'text/plain':
        text = flask.request.data.decode('utf-8')
        text = io.StringIO(text)
        text.seek(0)
        text = text.read()
    else:
        return flask.Response(response='This predictor only supports text data', status=415, mimetype='application/json')

    print('Invoked with: {}'.format(text))


    class_names = ['not hate','hate']
    model = Detoxify("original")
    model.model.cpu()

    def predictor(texts):
        logits = model.model(**model.tokenizer(texts, return_tensors="pt", truncation=True, padding=True ))[0][:, 0]
        score = torch.sigmoid(logits).detach().numpy()
        if isinstance(texts, list) and len(texts) > 1:
            score = score.reshape(-1, 1)
            scores = np.concatenate([1 - score, score], 1)
            return scores
        else:
            scores = np.expand_dims(np.array([1 - score, score]), 0).reshape(-1, 2)
            return scores

    explainer = LimeTextExplainer(class_names=class_names)

    exp = explainer.explain_instance(text, predictor, num_features=20, num_samples=10)
    output = dict(exp.as_list())
    print(output)
    output = flask.jsonify(output)
    del model

    return output