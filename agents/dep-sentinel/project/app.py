"""Sample Flask application that uses vulnerable dependencies.

This file is NEVER modified by the agent. It exists so the harness can
check compatibility — if a dependency is removed or replaced, the harness
verifies that all imports still resolve.
"""
from flask import Flask, jsonify, request as flask_request
import requests
import yaml
from cryptography.fernet import Fernet
from PIL import Image
from sqlalchemy import create_engine, text
import jinja2
import numpy as np
import pandas as pd
import click
from markupsafe import Markup
from werkzeug.utils import secure_filename
import redis
import celery
import boto3
from dotenv import load_dotenv
import gunicorn

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/process", methods=["POST"])
def process():
    data = yaml.safe_load(flask_request.data)
    df = pd.DataFrame(data.get("items", []))
    result = np.mean(df["value"].values) if len(df) > 0 else 0
    return jsonify({"mean": float(result)})


if __name__ == "__main__":
    app.run()
