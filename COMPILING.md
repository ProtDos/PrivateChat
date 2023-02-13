# Private Chat | Encochat
## Compiling Guide

### Important note:
It is important that you use a linux system. You can either use the Ubuntu Subsystem for Linux, a Linux VM or a Linux distribution.

You want to compile the app for yourself? Okay, here is how:

```
# Installing all the requirements
apt-get install python3
apt-get install python3-pip
pip3 install --user --upgrade buildozer
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.19 virtualenv

# Cloning the project
git clone https://github.com/ProtDos/PrivateChat/Test4
cd PrivateChat/Test4
export PATH=$PATH:~/.local/bin/

# Compiling :)
buildozer android debug deploy run
```
The compiling process is done, when you see continious blue text. Now press `Ctrl+C` to interrupt it.

```
# For Ubuntu system on Windows:
cd bin/
ls
# the file there is your final project
# move it to your windows system:
mv [filename] /mnt/c/Users/[username]/Downloads
```
Now connect your phone to your computer and allow file transfer. You can now drag and drop the file from your Downloads folder to your Android phone. Now open your explorer on your phone and tap on the app to install it. Easy as that.

## Errors
If you encounter any error, please don't hesitate to open an issue.
