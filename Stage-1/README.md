# Linux User Creation Bash Script
I was tasked with writing a bash script called `create_users.sh` that reads a **text file** containing the **usernames** and **group names** of new employees where each is written in the following format: `user;groups`. 

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








