sudo yum install -y epel-release
sudo yum install -y wget hping3 iperf3 tmux 'libasound*'
sudo yum install -y libXcomposite libXcursor libXi libXrandr xdg-utils nss GConf2 cups redhat-lsb-core-4.1-27.el7.centos.1.x86_64 gtk3 libXScrnSaver libXdamage libXtst
sudo yum remove -y google-chrome
sudo yum install -y Xvfb libXfont xorg-x11-fonts-misc.noarch xorg-x11-fonts-ethiopic.noarch xorg-x11-fonts-cyrillic.noarch xorg-x11-fonts-Type1.noarch xorg-x11-fonts-ISO8859-9-75dpi xorg-x11-fonts-ISO8859-9-100dpi screen lrzsz
sudo yum install -y xorg-x11-fonts-100dpi.noarch xorg-x11-fonts-75dpi.noarch xorg-x11-fonts-ISO8859-1-100dpi.noarch xorg-x11-fonts-ISO8859-1-75dpi.noarch xorg-x11-fonts-ISO8859-14-100dpi.noarch xorg-x11-fonts-ISO8859-14-75dpi.noarch xorg-x11-fonts-ISO8859-15-100dpi.noarch xorg-x11-fonts-ISO8859-15-75dpi.noarch xorg-x11-fonts-ISO8859-2-100dpi.noarch xorg-x11-fonts-ISO8859-2-75dpi.noarch
sudo yum install -y unzip
sudo yum install -y nscd

if [ ! -f google-chrome-stable_current_x86_64_63.0.3239.84.rpm ]; then
	wget 23.106.133.19/google-chrome-stable_current_x86_64_63.0.3239.84.rpm
fi
sudo rpm -ivh google-chrome-stable_current_x86_64_63.0.3239.84.rpm
if [ ! -f get-pip.py ]; then
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	sudo python get-pip.py
fi
if [ ! -f chromedriver_linux64.zip ]; then
	wget 23.106.133.19/chromedriver_linux64.zip
	unzip chromedriver_linux64.zip
fi

sudo pip install selenium
sudo pip install pyvirtualdisplay
sudo pip install numpy

echo finished
