Title: Running ROS on Windows 10
Date: 2017-10-23 10:00

Robot Operating System is a flexible framework for writing robot software. It is widely used all around the world and has become the industry standard for robotics. With a vast collection of tools, libraries and task simplifying conventions you can build software under a wide variety of robotic platforms. And today, we will learn how to install this “linux only” thing on Windows 10.

### Prequisites

You might have already heard about the Windows 10 creator update feature called `Windows Subsystem for Linux`. This is a new thing that allows you to run linux command-line tools from your PowerShell, while still using Windows desktop and apps. It is mostly a tool for developers, but since we want to play with robots, I guess this is who we are! Let’s start with checking, if you have what it takes to start developing linux applications.

### Check your updates

First we need to check, if we are eligible to install WSL:

- Go to Settings -> System -> About
- You need to have creators update installed (version 1703),
- You must run a 64-bit distribution.

### Enable developer mode

Steps you must take:

- Go to Settings -> Update & security -> For developers
- Check the “Developer mode” radio button.
- Allow the system to download whatever is needed.

### Install the Linux Subsystem

- Run Powershell as Administrator (this is important),
- Paste the following command:
    - `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
- Reboot when prompted.
- Open Powershell again and type in: `bash`
- Accept everything you must and here you go. You have the WSL installed.

Now we are ready to install the Robot Operating System on our Windows PC.

## Installing ROS

We will be installing ROS Lunar. For more information about distributions visit the ROS Distributions wiki page. For a good start, let’s update our sources:

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
```

Add keys:

```bash
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
```

Update your apt-get:

```bash
sudo apt-get update
```

Download the full desktop package of ROS Lunar:

```bash
sudo apt-get install ros-lunar-desktop-full
```

Initialize `rosdep`:

```bash
sudo rosdep init
rosdep update
```

Add your ROS variables to source:

```bash
echo "source /opt/ros/lunar/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

And… you are ready to go! Have fun working with robotics on Windows 10!
