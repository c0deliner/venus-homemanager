#!/bin/bash
echo "Installing Home Manager dbus bridge..."
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Generate start and stop scripts.."
# Kill script
echo "#!/bin/bash" > "$SCRIPT_DIR/kill_me.sh"
echo "kill \$(pgrep -f \"python $SCRIPT_DIR/dbus-homemanager.py\")" >> "$SCRIPT_DIR"/kill_me.sh

# Run script
echo "#!/bin/bash" > "$SCRIPT_DIR/service/run"
echo "python3 $SCRIPT_DIR/dbus-homemanager.py" >> "$SCRIPT_DIR"/service/run

echo "Marking files as executable.."
chmod +x "$SCRIPT_DIR/dbus-homemanager.py"
chmod +x "$SCRIPT_DIR/kill_me.sh"
chmod +x "$SCRIPT_DIR/service/run"

echo "Register service..."
ln -s "$SCRIPT_DIR/service" /service/venus-homemanager
if [ ! -f "/data/rc.local" ]; then
  # Create rc.local if not existing
  echo "#!/bin/bash" > /data/rc.local
  chmod +x /data/rc.local
fi
echo "ln -s $SCRIPT_DIR/service /service/venus-homemanager" >> /data/rc.local

echo "Installation finished!"