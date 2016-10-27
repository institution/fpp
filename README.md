Futerało Pokrywacz Profilem - Instrukcja Instalacji
---------------------------------------------------

```bash
# install prerequisites
sudo apt-get install python3 python3-numpy python3-matplotlib

# download
wget -O fpp.zip  https://github.com/institution/fpp/archive/master.zip
unzip -o fpp.zip
cd fpp-master

# install in system path - will write to /usr/local/bin/fpp
sudo sh ./install_path.sh

# test - should display version and usage
fpp

```
