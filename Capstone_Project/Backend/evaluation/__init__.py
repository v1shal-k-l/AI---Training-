"""
Offline evaluation of the AI assistant with mlflow.genai.evaluate().

    dataset.py   - the test questions ("exam paper") and what we expect for each
    scorers.py   - the markers that grade each answer
    run_eval.py  - runs the exam and logs results to MLflow

Run from the Backend folder:  python -m evaluation.run_eval
"""
