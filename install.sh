#!/bin/bash

echo "Installing Home Manager dbus bridge..."
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Marking files as executable.."
chmod +x $SCRIPT_DIR/dbus-homemanager.py
chmod +x $SCRIPT_DIR/kill_me.sh
chmod +x $SCRIPT_DIR/service/run

echo "Register service..."
ln -s $SCRIPT_DIR/service /service/venus-homemanager
if [ ! -f "/data/rc.local" ]; then
  echo "#!/bin/bash" > /data/rc.local
fi
echo "ln -s $SCRIPT_DIR/service /service/venus-homemanager" >> /data/rc.local

echo "Installation finished!"