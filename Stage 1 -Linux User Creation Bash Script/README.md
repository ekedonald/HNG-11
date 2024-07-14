# Linux User Creation Bash Script

## Introduction

A company that continues to expand its workforce needs a seamless and efficient onboarding solution for new employees. This involves user, group, security and log management.

Managing many users and groups in a Linux environment is a monotonous task. A simplified approach is to automate the process using a bash script.

## Overview

This project is based on writing a bash script called `create_users.sh` that reads a **text file** containing the **usernames** and **group names** of the new employees where each is written in the following format: `user;groups`.

### Prerequisites
* Ubuntu OS

## Features

1. Create users and groups as specified in the text file.
2. Sets up home directories with appropriate permissions and ownership.
3. Generates random passwords for the users.
4. Logs all actions to `/var/log/user_management.log`.
5. Stores the generated passwords securely in `/var/secure/user_passwords.txt`.
6. Ensures error handling for scenarios like existing users providing clear documentation and comments.

Checkout the [create_users.sh](./create_user.sh) script here.

## The Breakdown Of The `create_users.sh` Script

The following is a detailed breakdown of the `create_users.sh` script:

#### 1. Superuser Privileges Check

The conditional statement above is used to verify if the user executing the script has superuser user privileges. The root user has an Effective User ID `$EUID` of `0`. This simply means the script will executed only by a user with super user privileges.

```sh
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Use sudo."
    exit 1
fi
```

#### 2. Input File Check

This checks if an input file was provided when executing the command and displays a hint.

```sh
if [ -z "$1" ]; then
    echo "No input file provided"
    echo "Hint: sudo bash create_user.sh <input_file_>"
    exit 1
fi
```

#### 3. Variable Declaration

`input_file="$1"`: Assigns the first positional parameter to **input_file** which represents the file containing the employees usernames and group names. `log_file="/var/log/user_management.log"`: Sets the path where actions will be logged. `password_file="/var/secure/user_passwords.csv"`: Sets the path where the passwords will be logged.

 ```sh
 input_file="$1"
log_file="/var/log/user_management.log"
password_file="/var/secure/user_passwords.csv"
 ```

#### 4. Create Log & Password Files With File Permissions If They Do Not Exist

`touch $log_file`: Creates a log file. `mkdir -p /var/secure`: Creates the directory where the password files will be stored. `touch $password_file`: Creates a password file. `chmod 600 $password_file`: Assigns read and write permissions to only the user.

```sh
touch $log_file
mkdir -p /var/secure
touch $password_file
chmod 600 $password_file
```

#### 5. Logging Function & Password Generation Function

The **log_action** function creates a log message prefixed with the current date and time.

```sh
log_action() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a $log_file
}
```

The **generate_password** function creates a random password with 15 characters ranging from (a-z, A-Z and 0-9).

```sh
generate_password() {
    tr -dc A-Za-z0-9 </dev/urandom | head -c 15
}
```

#### 6. Read Input File & Remove Whitespace

`while IFS=';' read -r raw_username raw_groups; do`: Initiates a loop to read the input file, spit each line into **raw_username** and **raw_groups** using `;` as the delimiter. `username=$(echo "$raw_username" | xargs)` and `groups=$(echo "$raw_groups" | xargs)`: Removes whitespace from **raw_username** and **raw_groups** and assign them to **username** and **groups** respectively.

```sh
while IFS=';' read -r raw_username raw_groups; do
    # Remove whitespace
    username=$(echo "$raw_username" | xargs)
    groups=$(echo "$raw_groups" | xargs)
```

#### 7. Validate Username & Groups

This validates if **username** and **groups** are not empty. It either is empty, it'll log an error and skips.

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

#### 8. Group Creation

`IFS=',' read -ra group_list <<< "$groups"`: Splits groups into an array **group_list** using `,` as the delimiter. It loops through each group in group_list removing whitespace and checks if each group exists. If a group does not exist, `! getent group "$group" > /dev/null 2>&1` creates the group and logs the action.

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

#### 9. User Creation

`! id "$username" > /dev/null 2>&1;`: Check if a **username** does not exist. If the user does not exist, it creates the user with `useradd -m -s /bin/bash -G "$groups" "$username"`.

* `-m`: Creates the user's home directory.

* `-s /bin/bash`: Sets the user's default shell to **/bin/bash**.

* `-G "$groups"`: Adds the user to specified groups.

If the user already exists, it logs a message indicating the user exists.

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


#### 10. User Home Directory Permissions & Ownership

```sh
chmod 700 /home/"$username"
chown "$username:$username" /home/"$username"
log_action "Permissions set for user $username's home directory"
```

This sets `rwx` permissions, user and group ownership to the user's home directory.

## Implementation Of The Linux User Creation Bash Script

Log into your Ubuntu server and take the following steps to create and verify the functionality of the `create_users.sh` script:

1. Create the `create_users.sh` then copy and paste the content of this [file](https://github.com/ekedonald/Linux-User-Creation-Bash-Script/blob/main/create_users.sh) into the script.


2. Assign executable permissions to the `create_users.sh` file.

```sh
chmod +x create_users.sh
```

3. Create a file that contains the usernames and groups the employees belong to.

```sh
cat <<EOF | tee developers.txt
light; sudo,dev,www-data
idimma; sudo
mayowa; dev,www-data
ikenna; dev,prod
eke; prod
EOF
```

4. Run the `create_users.sh` script.

```sh
sudo bash create_users.sh developers.txt
```

![run script](./images/1%20run%20script.png)

5. Verify if the users have been created.

```sh
cat /etc/passwd | tail -5
```

![verify users](./images/1%20verify%20if%20users%20exist.png)

6. Inspect the log and password files.

```sh
sudo cat /var/log/user_management.log
```

![inspect log file](./images/1%20inspect%20log%20file.png)

```sh
sudo cat /var/secure/user_passwords.csv
```

![inspect password_file](./images/1%20password_file.png)

7. Check the groups users belong to.

```sh
groups light idimma mayowa
```

![check groups users belong to](./images/1%20check%20group%20users%20belong%20to.png)

## Conclusion

The `create_user.sh` script makes the management of users and groups seamless. Hence, the onboarding process for new employees is swift and efficient.