# Deploy to Oracle Cloud (Always Free Tier)

## Steps:

1. **Create account:** Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
   - Truly "Always Free" tier
   - No credit card charges

2. **Create VM Instance:**
   - Go to Compute → Instances → Create Instance
   - Choose "Always Free-eligible" shape (VM.Standard.E2.1.Micro)
   - OS: Ubuntu 22.04

3. **Connect via SSH:**
   ```bash
   ssh ubuntu@your-instance-ip
   ```

4. **Setup:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python
   sudo apt install python3-pip python3-venv -y

   # Clone your repo
   git clone https://github.com/yourusername/calaitgbot.git
   cd calaitgbot

   # Create venv and install
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Create .env file
   nano .env
   # Add your API keys
   ```

5. **Run as service (systemd):**
   ```bash
   sudo nano /etc/systemd/system/calbot.service
   ```

   Add:
   ```ini
   [Unit]
   Description=Calorie Tracker Telegram Bot
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/calaitgbot
   ExecStart=/home/ubuntu/calaitgbot/venv/bin/python bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable calbot
   sudo systemctl start calbot
   sudo systemctl status calbot
   ```

**Pros:**
- 100% free forever
- True 24/7 uptime
- Full control (root access)
- 2 VMs allowed on free tier

**Cons:**
- More complex setup
- Requires some Linux knowledge
