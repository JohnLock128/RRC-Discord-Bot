# This file is intended to be added to a raspberry pi crontab to keep the bot running and allow auto updates using GitHub

# Set the path to your Git repository
repo_path="/home/RRC-Bot/Desktop/RRC-Discord-Bot"
script="Google_interact.py"

# Navigate to the Git repository directory
cd "$repo_path" || exit 1

# Run the Python script
python3 Google_interact.py