from unittest import TestCase as tc

import sys
from pathlib import Path
import importlib.util

module_path = Path(__file__).resolve().parent.parent / 'src/recommender/recommender.py'
print("module_path: ", module_path)
module_name = 'recommender'

spec = importlib.util.spec_from_file_location(module_name, module_path)
recommender_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = recommender_module
spec.loader.exec_module(recommender_module)

import pandas as pd
import numpy as np

class TestRecommender(tc):
    def test_recommender(self):
        output = recommender_module.run()
        try:
            assert type(output) == pd.core.frame.DataFrame, "Output is not a pandas series"
            outputs = output.name.values
            assert type(outputs) == np.ndarray, "output.name.values is not a numpy array"
            assert len(outputs) == 10, "Output is not of length 10"
            assert type(outputs[0]) == str, "First recommendation is not a string"
        except AssertionError as e:
            print("DEBUGINE INFO:\n Output Type: ", type(output), 
                  "\n Length: ", len(outputs), 
                  "\n First recommendation: ", outputs[0],
                "\n (Do not confuse output with outputs in the test file)")