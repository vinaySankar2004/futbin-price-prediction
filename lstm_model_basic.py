import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Load data
data = pd.read_csv("../joined_player_data.csv")

# Preprocessing
data['date'] = pd.to_datetime(data['date'])
data = data.sort_values(['card_id', 'date'])  # Group by 'card_id' and sort by date

# Handle missing values
data.fillna(0, inplace=True)  # Replace missing values with 0

# Encode categorical features
label_encoders = {}
categorical_features = ['foot', 'work_rate', 'accelerate', 'nation', 'league', 'club', 'body_type', 'playstyles']
for feature in categorical_features:
    le = LabelEncoder()
    data[feature] = le.fit_transform(data[feature].astype(str))
    label_encoders[feature] = le

# Scale numerical features
scaler = MinMaxScaler()
numerical_features = [
    'rating', 'skill_moves', 'weak_foot', 'pace_m', 'acceleration', 'sprint_speed', 'shooting_m',
    'att_position', 'finishing', 'shot_power', 'long_shots', 'volleys', 'penalties', 'passing_m',
    'vision', 'crossing', 'fk_accuracy', 'short_pass', 'long_pass', 'curve', 'dribbling_m', 'agility',
    'balance', 'reactions', 'ball_control', 'dribbling', 'composure', 'defending_m', 'interceptions',
    'heading_acc', 'def_aware', 'stand_tackle', 'slide_tackle', 'physical_m', 'jumping', 'stamina',
    'strength', 'aggression', 'height', 'weight', 'total_ingame_stats', 'price'
]
data[numerical_features] = scaler.fit_transform(data[numerical_features])

# Combine all features (categorical + numerical)
all_features = numerical_features + categorical_features

# Prepare time series sequences
sequence_length = 10  # Number of past days to use for prediction
target = 'price'

sequences = []
targets = []

for player_id, group in data.groupby('card_id'):
    for i in range(len(group) - sequence_length):
        seq = group[all_features].iloc[i:i+sequence_length].values
        sequences.append(seq)
        targets.append(group[target].iloc[i+sequence_length])

sequences = np.array(sequences)
targets = np.array(targets)

# Split into training and validation sets
train_size = int(len(sequences) * 0.8)
X_train, X_val = sequences[:train_size], sequences[train_size:]
y_train, y_val = targets[:train_size], targets[train_size:]

# Build LSTM Model
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(sequence_length, len(all_features))),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1)  # Predicting price
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train model
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[early_stopping]
)

# Evaluate model
loss, mae = model.evaluate(X_val, y_val)
print(f"Validation Loss: {loss}, MAE: {mae}")

# Save the model
model.save("lstm_price_forecasting.h5")
