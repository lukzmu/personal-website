Title: Setup WSL for Data Science in Windows
Date: 2019-10-03 10:00

Let’s be honest - I’m not a Windows user, but sometimes you might get to a point where you are going to need a Windows machine for your daily Data Science tasks. With the support for Ubuntu, thanks to Windows Subsystem for Linux (WSL), I tried to make everything - between django and data science - work together and today I want to share how I made it happen.

This tutorial is divided into a few steps: installing the WSL, pimping it up with Anaconda Python distribution, setting up VSCode to work with bash instead of Powershell and setting up Docker to host our Data Science projects. Let’s get right to it!

## Install WSL

To install WSL on your PC you first need to enable it on your machine. To do that, you need to start Powershell as Administrator and run the following command (you will need to restart your computer when prompted):

```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

After you do this step, you need to go to the Microsoft Store app and install any distribution of Linux, for my case it was Ubuntu 18.04 LTS. Once you go through the installation process and set up your bash credentials you are good to go. Mind that you don’t need to use the provided Ubuntu Console app as the `bash` command activates WSL in any command terminal.

## Get Anaconda

I found a way to install the Anaconda distribution easily on WSL. First of all you need to figure out which anaconda release you want. A list of Anaconda installers is available here (remember to pick a Linux installer!):

- [Anaconda Installer archive](https://repo.anaconda.com/archive/)

Now that you have picked your version you need to run the following command:

```python
wget https://repo.continuum.io/archive/{SELECTED VERSION}

# Example:
# wget https://repo.continuum.io/archive/Anaconda3-2019.07-Linux-x86_64.sh
```

Now you need to run the installation script:

```python
bash {SELECTED VERSION}.sh

# Example:
# bash Anaconda3-2019.07-Linux-x86_64.sh
```

You will have to go through the license agreement (just hold ENTER, I don’t believe you will read those anyway) and at the end you will need to agree to it by writing `yes`.

Now reopen your terminal and run `which python` to see if this worked!

## Setup Visual Studio Code

Assuming you have Visual Studio Code installed on your Windows machine, we need to run it and change the following setting:

```bash
"terminal.integrated.shell.windows": "C:\\WINDOWS\\sysnative\\bash.exe"
```

Right now, every time you run the terminal in VSCode you should get the bash console. I still have to figure out how to load a specific WSL Anaconda environment when it starts (depending on the opened project), but once you activate it manually everything should work just fine.

You should also install the following addons:

- Python
- Remote - WSL

## Making Docker work

Last step everyone! Making Docker for Windows work with our WSL distribution. First of all, we need to expose the Daemon on tcp (mind that this is without TLS, so in theory you might be vulnerable to remote attacks. In practice, for local developement this won’t be an issue).

We want to add the docker host to our bash source, so it connects to our daemon every time we open the terminal (a nice quality of life thing, you don’t need to do this):

```bash
echo "export DOCKER_HOST=tcp://localhost:2375" >> ~/.bashrc
source ~/.bashrc
```

### Installing Docker and Docker-Compose

To push our changes to docker containers, we need to create a Dockerfile or a docker-compose. So let’s install both! As described in the Docker Ubuntu installation documentation we need to do the following to install Docker:

1. Update the apt package index

```bash
sudo apt-get update
```

2. Install packages to allow apt to use a repository over HTTPS

```bash
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
```

3. Add Docker’s official GPG key

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

4. Verify that you now have the key with the fingerprint `9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88`, by searching for the last 8 characters of the fingerprint

```bash
sudo apt-key fingerprint 0EBFCD88
```

5. Use the following command to set up the stable repository. To add the nightly or test repository, add the word `nightly` or `test` (or both) after the word stable in the commands below

```bash
sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) \
stable"
```

6. Update the apt package index

```bash
sudo apt-get update
```

7. Install the latest version of Docker Engine - Community and containerd

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

8. If you would like to use Docker as a non-root user, you should now consider adding your user to the “docker” group with something like the following:

```bash
sudo usermod -aG docker your-user
```

9. nally we can install `docker-compose`. If you want to install that under some specific env, remember to `conda avtivate` it first.

```bash
conda install -c conda-forge docker-compose

# If you want to use pip instead:
# pip install docker-compose
```

### Fixing drive mounting

If you want your drives mounted as `/c` or `/d` instead of `/mnt/c` or `/mnt/d` (and you probably do, because some scripts might go crazy over that), you need to modify the WSL configuration file. Open it using the following command: `sudo nano /etc/wsl.conf` and add the following:

```
[automount]
root = /
options = "metadata"
```

### Active Directory fuckup help

If you are logged in as an **Active Directory** user, life won’t be easy for you. You will notice that you can’t share drives with Docker as the user credentials are invalid. I found only one solution to this and it’s a bit hacky: you need to create a local user with the same name as the ActiveDirectory one… Hey, it works!
