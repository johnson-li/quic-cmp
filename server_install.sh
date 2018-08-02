sudo yum install -y wget
wget https://www.golangtc.com/static/go/1.9.2/go1.9.2.linux-amd64.tar.gz
tar zxf go1.9.2.linux-amd64.tar.gz
mkdir gowork
mkdir gowork/src
mkdir gowork/bin
mkdir gowork/pkg
export PATH=$PATH:/home/johnsonli1993/go/bin
export GOPATH=/home/johnsonli1993/gowork
export PATH=$PATH:$GOPATH/bin
go get github.com/mholt/caddy/caddy
go get github.com/caddyserver/builds
go run gowork/src/github.com/mholt/caddy/caddy/build.go
mkdir websites
wget -P /home/johnsonli1993/gowork/src/github.com/mholt/caddy/caddy 23.106.133.19/Caddyfile
wget 23.106.133.19/certificate.crt
wget 23.106.133.19/private.key
wget -P /home/johnsonli1993/websites 23.106.133.19/mama.cn.zip
sudo yum install -y unzip
unzip /home/johnsonli1993/websites/mama.cn.zip -d /home/johnsonli1993/websites/
