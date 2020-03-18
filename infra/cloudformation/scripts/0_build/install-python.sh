sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt purge python2.7-minimal
sudo apt install -y python3.7
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py