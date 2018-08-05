wget 23.106.133.19/google-chrome-stable_current_x86_64_63.0.3239.84.rpm
sudo yum install -y wget hping3 iperf3 tmux
sudo yum install -y libXcomposite libXcursor libXi libXrandr xdg-utils nss GConf2 cups redhat-lsb-core-4.1-27.el7.centos.1.x86_64 gtk3 libXScrnSaver libXdamage libXtst
sudo yum remove -y google-chrome
sudo rpm -ivh google-chrome-stable_current_x86_64_63.0.3239.84.rpm
sudo yum install -y Xvfb libXfont xorg-x11-fonts-misc.noarch xorg-x11-fonts-ethiopic.noarch xorg-x11-fonts-cyrillic.noarch xorg-x11-fonts-Type1.noarch xorg-x11-fonts-ISO8859-9-75dpi xorg-x11-fonts-ISO8859-9-100dpi screen lrzsz
sudo yum install -y xorg-x11-fonts-100dpi.noarch xorg-x11-fonts-75dpi.noarch xorg-x11-fonts-ISO8859-1-100dpi.noarch xorg-x11-fonts-ISO8859-1-75dpi.noarch xorg-x11-fonts-ISO8859-14-100dpi.noarch xorg-x11-fonts-ISO8859-14-75dpi.noarch xorg-x11-fonts-ISO8859-15-100dpi.noarch xorg-x11-fonts-ISO8859-15-75dpi.noarch xorg-x11-fonts-ISO8859-2-100dpi.noarch xorg-x11-fonts-ISO8859-2-75dpi.noarch
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py
sudo pip install selenium
sudo pip install pyvirtualdisplay
sudo pip install numpy
wget 23.106.133.19/google-chrome-stable_current_x86_64_63.0.3239.84.rpm
git clone https://github.com/jiaxintang/plt-conn_test.git
mv plt-conn_test mypagetest
wget 23.106.133.19/chromedriver_linux64.zip
sudo yum install -y unzip
unzip chromedriver_linux64.zip
