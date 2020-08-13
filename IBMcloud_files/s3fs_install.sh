# Reference: https://github.com/MIDS-scaling-up/v2/tree/master/week02/lab2

sudo apt-get update
sudo apt-get install automake autotools-dev g++ git libcurl4-openssl-dev libfuse-dev libssl-dev libxml2-dev make pkg-config
git clone https://github.com/s3fs-fuse/s3fs-fuse.git

cd ./s3fs-fuse
./autogen.sh
./configure
make
sudo make install