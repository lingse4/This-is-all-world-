import torch
flag = torch.cuda.is_available()
print(f"GPU是否可用：{flag}")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
print(torch.cuda.get_device_name(0))
