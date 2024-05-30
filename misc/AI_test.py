import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

def preprocess_data(df: pd.DataFrame) -> tuple:
    """Preprocess the data"""
    # Convert Start and End columns to string format
    df['Start'] = df['Start'].astype(str)
    df['End'] = df['End'].astype(str)

    # Split Start and End columns into hours, minutes, and seconds
    df[['Start_hours', 'Start_minutes', 'Start_seconds']] = df['Start'].apply(lambda x: pd.Series(x.split(':')))
    df[['End_hours', 'End_minutes', 'End_seconds']] = df['End'].apply(lambda x: pd.Series(x.split(':')))

    # Convert Start and End columns to seconds
    df['Start'] = df['Start_hours'].astype(int) * 3600 + df['Start_minutes'].astype(int) * 60 + df['Start_seconds'].astype(int)
    df['End'] = df['End_hours'].astype(int) * 3600 + df['End_minutes'].astype(int) * 60 + df['End_seconds'].astype(int)

    # Drop the Actor-Action, VideoID, Usage, Start_hours, Start_minutes, Start_seconds, End_hours, End_minutes, and End_seconds columns from the DataFrame
    X = df.drop(['Actor-Action', 'VideoID', 'Usage', 'Start_hours', 'Start_minutes', 'Start_seconds', 'End_hours', 'End_minutes', 'End_seconds'], axis=1)

    # Create the target variables for activity and actor
    y_activity = df['Actor-Action']
    y_actor = y_activity.apply(lambda x: x.split('-')[0])

    return X, y_activity, y_actor

def train_model(X: pd.DataFrame, y: pd.Series, model_type: str) -> RandomForestClassifier:
    """Train a random forest classifier"""
    rfc = RandomForestClassifier(n_estimators=100, random_state=42)
    if model_type == 'activity':
        X = X.drop(['Width', 'Height', 'Area'], axis=1)
    rfc.fit(X, y)
    return rfc

def evaluate_model(rfc: RandomForestClassifier, X: pd.DataFrame, y: pd.Series) -> None:
    """Evaluate the model"""
    y_pred = rfc.predict(X)
    print(f"{rfc.__class__.__name__} accuracy:", accuracy_score(y, y_pred))
    print(f"{rfc.__class__.__name__} classification report:")
    print(classification_report(y, y_pred))
    print(f"{rfc.__class__.__name__} confusion matrix:")
    print(confusion_matrix(y, y_pred))

def main() -> None:
    file_path = 'train_data/videoset.csv'
    df = pd.read_csv(file_path)
    print(df.columns)
    X, y_activity, y_actor = preprocess_data(df)

    X_train, X_test, y_train_activity, y_test_activity = train_test_split(X, y_activity, test_size=0.2, random_state=42)
    X_train_actor, X_test_actor, y_train_actor, y_test_actor = train_test_split(X, y_actor, test_size=0.2, random_state=42)

    rfc_activity = train_model(X_train, y_train_activity, 'activity')
    evaluate_model(rfc_activity, X_test.drop(['Width', 'Height', 'Area'], axis=1), y_test_activity)

    rfc_actor = train_model(X_train_actor, y_train_actor, 'actor')
    evaluate_model(rfc_actor, X_test_actor.drop(['Width', 'Height', 'Area'], axis=1), y_test_actor)

    joblib.dump(rfc_activity, 'activity_recognition_model.joblib')
    joblib.dump(rfc_actor, 'actor_recognition_model.joblib')

if __name__ == '__main__':
    main()