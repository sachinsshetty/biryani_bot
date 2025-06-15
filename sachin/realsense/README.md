Realsense - D430

sudo apt-get update
sudo apt-get install git libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev \
    libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev python3-pip
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
mkdir build && cd build
cmake ../ -DFORCE_RSUSB_BACKEND=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON_BINDINGS=true
make -j$(nproc)
sudo make install


sudo cp ../config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger


export PYTHONPATH=$PYTHONPATH:/usr/local/lib


python3.10 -m venv venv
source venv/bin/activate

pip install pyrealsense2 numpy opencv-python dwani paho-mqtt


python world_state.py

-- 

MQTT server

sudo apt install mosquitto mosquitto-clients -y

sudo systemctl status mosquitto