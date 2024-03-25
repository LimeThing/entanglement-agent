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
    state = torch.tensor(state, dtype=torch.float)
    action = torch.tensor(state, dtype=torch.long)
    reward = torch.tensor(state, dtype=torch.float)
    next_state = torch.tensor(state, dtype=torch.float)

    if len(state.shape) == 1:
      state = torch.unsqueze(state, 0)
      next_state = torch.unsqueze(next_state, 0)
      reward = torch.unsqueze(reward, 0)
      action = torch.unsqueze(action, 0)
      done = (done, )

    # 1: predicted Q values using states
    pred = self.model(state)

    target = pred.clone()
    for index in range(len(done)):
      Q_new = reward[index]
      if not done:
        Q_new = reward[index] + self.gamma * torch.max(self.model(next_state[index])) 

      target[index][torch.argmax(action).item()] = Q_new # index of the action that is the biggest

    self.optimizer.zero_grad()
    loss = self.criterion(target, pred)
    loss.backward()

    self.optimiser.step()

    
