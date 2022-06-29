# venus-homemanager service
## Purpose
This service is meant to be run on VenusOS from Victron.

The script captures the multicast messages sent from the SMA Home Manager 2.0 and publishes the decoded
information on the dbus. It pretty much behaves like a Victron Grid Meter.

## Installation
Installation is kept nice and simple as the service brings its own installation script.
Just clone the branch and execute the installation script.
I recommend creating a subdirectory inside the `/data` directory to prevent VenusOS updates from deleting the service.

```
mkdir /data/drivers
cd /data/drivers
git clone --recurse-submodules https://github.com/c0deliner/venus-homemanager.git
cd venus-homemanager
chmod +x install.sh
./install.sh
```
