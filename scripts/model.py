"""
LSTM model for soil moisture forecasting.

Architecture: stacked LSTM encoder → FC head → scalar moisture prediction
"""

import torch
import torch.nn as nn

N_FEATURES = 4   # moisture, temperature, humidity, light


class MoistureLSTM(nn.Module):
    def __init__(
        self,
        input_size: int = N_FEATURES,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)
        last = out[:, -1, :]      # take last timestep
        return self.head(last).squeeze(-1)


def load_model(checkpoint_path: str, device: str = "cpu") -> MoistureLSTM:
    model = MoistureLSTM()
    state = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model
