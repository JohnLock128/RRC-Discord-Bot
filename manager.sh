# This file is intended to be added to a raspberry pi crontab to keep the bot running and allow auto updates using GitHub

# Set the path to your Git repository
repo_path="/home/RRC-Bot/Desktop/RRC-Discord-Bot"
main_script="BotMain.py"

# Navigate to the Git repository directory
cd "$repo_path" || exit 1

echo "Checking for updates..."
if git pull origin main | grep -q 'Already up to date'; then
    echo "No updates found."
else
    echo "Updates found. Stopping bot script..."
    
    # Stop the running script if it's still active
    pkill -f "$main_script"
    
    # Update the Git repository
    git pull origin main
    
    echo "Starting bot script..."
    
    # Start the bot script
    python3 "$main_script" &
fi

# Check if the bot script is running
if pgrep -f "$main_script" > /dev/null; then
    echo "Bot script is already running."
else
    echo "Bot script is not running. Starting..."
    
    # Start the bot script
    python3 "$main_script" &
fi
