import torch
import torch.nn as nn
import torch.optim as optin
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
  def __init__(self, input_size, hidden_size, output_size):
    super.__init__()
    self.linear1 = nn.Linear(input_size, hidden_size)
    self.linear2 = nn.Linear(hidden_size, output_size)

  def forward(self, x): # tensor
    x = F.relu(seld.linear1(x))
    x = self.linear2(x)
    return x

  def save(self, file_name="model.pth"):
      model_folder_path = "./model"
      if not os.path.exists(model_folder_path):
        os.makedirs(model_folder_path)

    file_name = os.path.join(model_folder_path, file_name)
    torch.save(self.state_dict(), file_name)

class QTrainer:
  def __init__(self, model, learning_rate, gamma):
    self.learning_rate = learning_rate
    self.gamma = gamma
    self.model = model
    self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    self.criterion = nn.MSELoss()

  def train_step(self, state, action, reward, next_state, done):
    pass
