# Linux User Creation Bash Script
This project is based on writing a bash script called `create_users.sh` that reads a **text file** containing the **usernames** and **group names** of the new employees where each is written in the following format: `user;groups`. 

The script performs the following functions:

1. Create users and groups as specified in the text file.
2. Set ups home directories with appropriate permissions and ownership.
3. Generates random passwords for the users.
4. Logs all actions to `/var/log/user_management.log`.
5. Stores the generated passwords securely in `/var/secure/user_passwords.txt`.
6. Ensures error handling for scenarios like existing users providing clear documentation and comments.

Checkout the [create_users.sh](./create_user.sh) script here.

## The Breakdown of The create_user.sh Script

The following is a detailed breakdown of the `create_user.sh` script:

#### Superuser Privileges Check

```sh
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Use sudo."
    exit 1
fi
```

The conditional statement above is used to verify if the user executing the script has superuser user privileges. The root user has an Effective User ID `$EUID` of `0`. 

This simply means the script will executed only by a user with super user privileges.

#### Input File Check

```sh
if [ -z "$1" ]; then
    echo "No input file provided"
    echo "Hint: sudo bash create_user.sh <input_file_>"
    exit 1
fi
```
 This checks if an input file was provided when executing the command and displays a hint.


 #### Variable Declaration

 ```sh
 input_file="$1"
log_file="/var/log/user_management.log"
password_file="/var/secure/user_passwords.csv"
 ```

 `input_file="$1"`: Assigns the first positional parameter to **input_file** which represents the file containing the employees usernames and group names.

 `log_file="/var/log/user_management.log"`: Sets the path where actions will be logged.

`password_file="/var/secure/user_passwords.csv"`: Sets the path where the passwords will be logged.

#### Create Log & Password Files With File Permissions If They Do Not Exist 

```sh
touch $log_file
mkdir -p /var/secure
touch $password_file
chmod 600 $password_file
```

#### Logging Function & Password Generation Function

```sh
log_action() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a $log_file
}
```
The **log_action** function creates a log message prefixed with the current date and time.

```sh
generate_password() {
    tr -dc A-Za-z0-9 </dev/urandom | head -c 15
}
```

The **generate_password** function creates a random password with 15 characters ranging from (a-z, A-Z and 0-9).


#### Read Input File & Remove Whitespace

```sh
while IFS=';' read -r raw_username raw_groups; do
    # Remove whitespace
    username=$(echo "$raw_username" | xargs)
    groups=$(echo "$raw_groups" | xargs)
```

`while IFS=';' read -r raw_username raw_groups; do`: Initiates a loop to read the input file, spit each line into **raw_username** and **raw_groups** using `;` as the delimiter.

`username=$(echo "$raw_username" | xargs)` and `groups=$(echo "$raw_groups" | xargs)`: Used to remove whitespace from **raw_username** and **raw_groups** and assign them to **username** and **groups** respectively.

#### Validate Username & Groups

```sh
  if [ -z "$username" ]; then
        log_action "Invalid or empty username found, skipping..."
        continue
    fi

    if [ -z "$groups" ]; then
        log_action "No groups specified for user $username, skipping..."
        continue
    fi
```

This validates if **username** and **groups** are not empty. It either is empty, it'll log an error and skips.


#### Group Creation

```sh
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
```

`IFS=',' read -ra group_list <<< "$groups"`: Splits groups into an array **group_list** using `,` as the delimiter. 

It then loops through each group in group_list removing whitespace and checks if each group exits. If a group does not exist, `! getent group "$group" > /dev/null 2>&1` creates the group and logs the action.

#### User Creation

```sh
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
```

`! id "$username" > /dev/null 2>&1;`: Check if a **username** does not exist. If the user does not exist, it creates the user with `useradd -m -s /bin/bash -G "$groups" "$username"`.

* `-m`: Creates the user's home directory.

* `-s /bin/bash`: Sets the user's default shell to **/bin/bash**.

* `-G "$groups"`: Adds the user to specified groups.

If the user already exists, it logs a message indicating the user exists.

#### User Home Directory Permissions & Ownership

```sh
chmod 700 /home/"$username"
    chown "$username:$username" /home/"$username"
    log_action "Permissions set for user $username's home directory"
```

This sets `rwx` permissions, user and group ownership to the user's home directory.

## Validate Bash Script

Log into your Ubuntu server and take the following steps to verify the functionality of the `create_user.sh` script:

1. Create the `create_user.sh` script using the following command.

```sh
cat <<EOF | tee create_user.sh
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
EOF
```

2. Assign executable permissions to the `create_user.sh` file.

```sh
chmod +x create_user.sh
```

3. Create a file that contains the usernames and groups the employees belong to.

```sh
cat <<EOF | tee developers.txt
light; sudo,dev,www-data
idimma; sudo
mayowa; dev,www-data
ikenna: dev,prod
eke: prod
EOF
```

4. Run the `create_user.sh` script.

```sh
sudo bash create_user.sh developers.txt
```

5. Verify if the users have been created.

```sh
cat /etc/passwd | tail -5
```

6. Inspect the log and password files.

```sh
sudo cat/var/log/user_management.log
```

```sh
sudo cat /var/secure/user_passwords.csv
```

7. Check the groups users belong to.

```sh
groups light idimma mayowa
```



