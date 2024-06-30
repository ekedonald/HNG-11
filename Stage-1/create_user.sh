#!/bin/bash

# Ensure the script is run with superuser privileges
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Use sudo."
    exit 1
fi

# Check if the input file is provided
if [ -z "$1" ]; then
    echo "No input file provided"
    echo "Hint: sudo bash create_user.sh <input_file_>"
    exit 1
fi

input_file="$1"
log_file="/var/log/user_management.log"
password_file="/var/secure/user_passwords.csv"

# Create log and password files if they do not exist
touch $log_file
mkdir -p /var/secure
touch $password_file
chmod 600 $password_file

# Function to log actions
log_action() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a $log_file
}

# Function to generate a random password
generate_password() {
    tr -dc A-Za-z0-9 </dev/urandom | head -c 15
}

# Read the input file line by line
while IFS=';' read -r raw_username raw_groups; do
    # Remove whitespace
    username=$(echo "$raw_username" | xargs)
    groups=$(echo "$raw_groups" | xargs)

    # Validate username and groups
    if [ -z "$username" ]; then
        log_action "Invalid or empty username found, skipping..."
        continue
    fi

    if [ -z "$groups" ]; then
        log_action "No groups specified for user $username, skipping..."
        continue
    fi

    # Create groups if they do not exist
    IFS=',' read -ra group_list <<< "$groups"
    for group in "${group_list[@]}"; do
        group=$(echo "$group" | xargs)  # Trim whitespace
        if [ -z "$group" ]; then
            log_action "Invalid or empty group name found for user $username, skipping..."
            continue
        fi

        if ! getent group "$group" > /dev/null 2>&1; then
            groupadd "$group"
            if [ $? -eq 0 ]; then
                log_action "Group $group created"
            else
                log_action "Failed to create group $group"
                continue
            fi
        fi
    done

    # Create user if they do not exist
    if ! id "$username" > /dev/null 2>&1; then
        useradd -m -s /bin/bash -G "$groups" "$username"
        if [ $? -eq 0 ]; then
            log_action "User $username created and added to groups $groups"

            # Generate and set password
            password=$(generate_password)
            echo "$username:$password" | chpasswd
            if [ $? -eq 0 ]; then
                log_action "Password set for user $username"

                # Store the password securely
                echo "$username:$password" >> $password_file
            else
                log_action "Failed to set password for user $username"
            fi
        else
            log_action "Failed to create user $username"
            continue
        fi
    else
        log_action "User $username already exists"
    fi

    # Set appropriate permissions for the user's home directory
    chmod 700 /home/"$username"
    chown "$username:$username" /home/"$username"
    log_action "Permissions set for user $username's home directory"
done < "$input_file"

log_action "User creation process completed"

exit 0
