Futerało Pokrywacz Profilem - Instrukcja Instalacji
---------------------------------------------------

```bash
# install prerequisites
sudo apt-get install python3 python3-numpy python3-matplotlib

# download
wget -O fpp-master.zip  https://github.com/institution/fpp/archive/master.zip
unzip -o fpp-master.zip

# install in system path - will write to /usr/local/bin/fpp
cd fpp-master
sudo sh ./install_path.sh
cd ..

# test - should display version and usage
fpp

```
