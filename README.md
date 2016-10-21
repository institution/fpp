```bash
# install prerequisites
apt-get install python3 python3-numpy

# download
wget https://github.com/institution/fpp/archive/master.zip
unzip master.zip
cd fpp-master

# install in system path
echo "python3 `pwd`/main.py \$*" > /usr/local/bin/fpp
chmod +x /usr/local/bin/fpp

# test - should display usage
fpp

```
