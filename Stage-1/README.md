# Linux User Creation Bash Script
I was tasked with writing a bash script called `create_users.sh` that reads a **text file** containing the **usernames** and **group names** of the new employees where each is written in the following format: `user;groups`. 

The script performs the following functions:

1. Create users and groups as specified in the text file.
2. Set ups home directories with appropriate permissions and ownership.
3. Generates random passwords for the users.
4. Logs all actions to `/var/log/user_management.log`.
5. Stores the generated passwords securely in `/var/secure/user_passwords.txt`.
6. Ensures error handling for scenarios like existing users providing clear documentation and comments.

Checkout the [create_users.sh](./create_user.sh) script here.

## The Breakdown of the create_user.sh script

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
password_file="/var/secure/user_passwords.txt"
 ```

 `input_file="$1"`: Assigns the first positional parameter to **input_file** which represents the file containing the employees usernames and group names.

 `log_file="/var/log/user_management.log"`: Sets the path where actions will be logged.

`password_file="/var/secure/user_passwords.txt"`: Sets the path where the passwords will be logged.

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


















