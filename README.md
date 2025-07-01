# Backup Integrity Check

Simple integrity check program that will enumerate files in a specified directory and create an output file with the file name and the corresponding SHA256 hash.

## Basic Usage
Example of generating hash values for user `foo` for all the files in the user's "Documents" directory:
`./buic.py -b ~/Documents`
or
`./buic.py -b /home/foo/Documents`
This will create a `backup_hashes.txt` file in whatever the current working directory the user is in.

Example of verifying files that have been restored from backup for user `foo` with restored files in "Documents" directory and the `backup_hashes.txt` file located in the user's home directory:
`./buic.py -v ~/Documents ~/backup_hashes.txt`
or
`./buic.py -v /home/foo/Documents /home/backup_hashes.txt`

## Detailed Instructions
### Setting up the optional dependencies
If you do not have termcolor module, make sure to download it for your system. On Linux system to install it system-wide run `sudo apt install python3-termcolor -y` or `sudo dnf install python3-termcolor -y` depending on your distribution. Ensure you have `git` installed as well: `sudo apt install git -y` or `sudo dnf install git -y`.

### Navigate to the directory where you want to save this script
In Linux, use your terminal to create and navigate to the directory where you want this script to be saved. Example `mkdir -p /home/[user_name]/applications && cd /home/[user_name]/applications` and make sure to replace '[user_name]' with the actual user on your system.

### Clone this repository and make it your working directory
`git clone https://github.com/bash-against-the-machine/backup-integrity-check.git && cd backup-integrity-check`

### Add execution permission to the python script
`chmod +x buic.py`

### Run the script
#### Creating hash values
You can run the script from a directory where you want the file containing the hashes to be saved, you just need to use either the absolute or user home directory file path. For example, to run it from the home folder of your user on the files located in the "Documents" directory you can do either:
`python3 /home/[user_name]/applications/backup-integrity-check/buic.py -b /home/[user_name]/Documents`
or
`python3 ~/applications/backup-integrity-check/buic.py`
The above code will execute the script enumerate all the files in the "Documents" folder of the user and calculate the SHA256 hash for each file. The output will be saved in the current working directory, in this case `/home[user_name]/backup_hashes.txt`
#### Verifying hash values
You can run the script from any directory, just make sure to use the absolute path of the script, the directory where the restored files are located, and the file path of the `backup_hashes.txt` file:
`python3 /home/[user_name]/applications/backup-integrity-check/buic.py -v /home/[user_name]/Documents /home/[user_name]/backup_hashes.txt`
#### Create an alias in Linux in lieu of file path of the script
Use Nano text editor to add an alias:
`nano ~/.bashrc`.

Add the following line to the end of the file (make sure to replace '[user_name]' with the name of the user you're logged in as):
`alias buic='/home/[user_name]/applications/backup-integrity-check/buic.py'`
Press CTRL+O to save the file, press ENTER key, then press CTRL+X to exit Nano editor. Close and relaunch the terminal. You can now substitute the file path of the `buic.py` script by simply typing `buic` followed by the -b or -v arguments and the directory/filepath.

<sub>Note: your `~/.basrc` file may say that the best practice is to keep aliases in a seprate `~/.bash_aliases` file. If that is the case then instead of running `nano ~/.bashrc` run `nano ~/.bash_aliases` and add the alias line in that file.</sub>