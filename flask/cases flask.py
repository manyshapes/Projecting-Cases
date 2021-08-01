from flask import Flask
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


# Setting features and targets
# x = df['date', 'location']

# X = df['date', 'location']
# y = df[ case counts column for one disease ].values.ravel()

app = Flask(__name__)

@app.route("/")
def return_this():
    return "<p> Place holder </p>"
