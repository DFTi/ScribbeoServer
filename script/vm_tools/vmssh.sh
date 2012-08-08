VM_HOST="app.scribbeo.com"
VM_USER="scribbeo"
HIVE_IP="app.scribbeo.com"
HIVE_LOCAL_VNC_PORT=5901
LOCAL_VNC_PORT=15951
HIVE_WAN_SSH_PORT=55218
HIVE_USER="hive"

function hive {
  ruby /Users/keyvan/Dropbox/DFT/Hive/Scripts/hive/secure_vnc_tunnel.rb $LOCAL_VNC_PORT $HIVE_IP $HIVE_LOCAL_VNC_PORT $HIVE_WAN_SSH_PORT $HIVE_USER
  echo "Entering SSH session ($HIVE_IP:$HIVE_WAN_SSH_PORT)"
  ssh -p $HIVE_WAN_SSH_PORT $HIVE_USER@$HIVE_IP
}

function hive_x11 {
  ssh -X -p $HIVE_WAN_SSH_PORT $HIVE_USER@$HIVE_IP
}

function vmssh {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  echo "Connecting to $VM_USER@$VM_HOST:$VM_PORT"
  ssh -p $VM_PORT $VM_USER@$VM_HOST
}

function vmscp {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  VM_SEND_FILE=$2
  echo "Sending $VM_SEND_FILE to $VM_USER@$VM_HOST:$VM_PORT:$VM_SEND_FILE"
  scp $VM_SEND_FILE scribbeo@$VM_ROOT$VM_INT:~/$VM_SEND_FILE
}

function vmscp-data {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  VM_SEND_FILE=$2
  echo "Sending $VM_SEND_FILE to $VM_USER@$VM_HOST:$VM_PORT:$VM_SEND_FILE"
  scp $VM_SEND_FILE scribbeo@$VM_ROOT$VM_INT:/home/curator/media/$VM_SEND_FILE
}

function vmdevices {
  VM_REMOTE_CMD='cd /opt/ScribbeoServer && script/devices'
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  echo "Retrieving device list for VM $1"
  ssh -p $VM_PORT $VM_USER@$VM_HOST $VM_REMOTE_CMD
}

function vmredeploy {
  VM_REMOTE_CMD='cd /opt/ScribbeoServer && script/redeploy'
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  echo "Updating source code & redeploying on  VM $1"
  ssh -t -p $VM_PORT $VM_USER@$VM_HOST $VM_REMOTE_CMD
  echo "Redeploy is complete!"
}
