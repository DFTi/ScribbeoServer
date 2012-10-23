SECURE_TUNNEL_RUBYSCRIPT="/Users/keyvan/Dropbox/DFT/Projects/ScribbeoServer/script/vm_tools/secure_tunnel.rb"
VM_HOST="app.scribbeo.com"
VM_USER="scribbeo"
HIVE_IP="app.scribbeo.com"
HIVE_LOCAL_VNC_PORT=5901
LOCAL_VNC_PORT=15951
LOCAL_SOCKS_PORT=10000
HIVE_WAN_SSH_PORT=55218
HIVE_USER="hive"

LOCAL_TURNER_VNC_PORT=15952
local_GITLAB_VNC_PORT=15953
remote_kvm_GITLAB_VNC_PORT=5904

local_WINDOWS_SERVER_VNC_PORT=15954
remote_kvm_WINDOWS_VNC_PORT=5905

HIVE_TURNER_PROXY_KVM_VNC_PORT=5904
HIVE_TURNER_PROXY_SSH_PORT=36641

function chicken_vnc_connect {
  osascript -e "tell application \"Chicken\" to activate
  tell application \"System Events\"
    keystroke \"n\" using {command down}
    keystroke \"localhost:$1\"
    keystroke return
  end tell"
}

alias turner_proxy="cd ~/Code/autovpn/ && ./start.sh"

function turner_vnc {
  ruby $SECURE_TUNNEL_RUBYSCRIPT $LOCAL_TURNER_VNC_PORT
  ssh -L $LOCAL_TURNER_VNC_PORT\:localhost\:5900 -N -f -l dftmacmini 10.185.49.2
  open vnc://localhost:$LOCAL_TURNER_VNC_PORT
}

function gitlab_vnc {
  ruby $SECURE_TUNNEL_RUBYSCRIPT $local_GITLAB_VNC_PORT
  ssh -L $local_GITLAB_VNC_PORT\:localhost\:$remote_kvm_GITLAB_VNC_PORT -p $HIVE_WAN_SSH_PORT -N -f -l $HIVE_USER $HIVE_IP
  chicken_vnc_connect $local_GITLAB_VNC_PORT
}

function gitlab_ssh {
  echo "Opening SSH connection to GITLAB VM on HIVE hypervisor"
  ssh keyvan@$HIVE_IP -p 36641
}

function windows_server_vnc {
  ruby $SECURE_TUNNEL_RUBYSCRIPT $local_WINDOWS_SERVER_VNC_PORT
  ssh -L $local_WINDOWS_SERVER_VNC_PORT\:localhost\:$remote_kvm_WINDOWS_VNC_PORT -p $HIVE_WAN_SSH_PORT -N -f -l $HIVE_USER $HIVE_IP
  chicken_vnc_connect $local_WINDOWS_SERVER_VNC_PORT
}

function hive_vnc {
  ruby $SECURE_TUNNEL_RUBYSCRIPT $LOCAL_VNC_PORT
  echo "Establishing VNC tunnel ($HIVE_IP:$HIVE_WAN_SSH_PORT)"  
  ssh -L $LOCAL_VNC_PORT\:localhost\:$HIVE_LOCAL_VNC_PORT -p $HIVE_WAN_SSH_PORT -N -f -l $HIVE_USER $HIVE_IP
  sleep 5
  echo "Launching Screen Sharing to $VM_HOST"
  open vnc://localhost:$LOCAL_VNC_PORT
  echo "Opening SSH connection with HTTP SOCKS proxy on $LOCAL_SOCKS_PORT"
  ssh -D $LOCAL_SOCKS_PORT $HIVE_USER@$HIVE_IP -p $HIVE_WAN_SSH_PORT
}

function hive_ssh {
  ruby $SECURE_TUNNEL_RUBYSCRIPT $HIVE_WAN_SSH_PORT
  echo "Opening SSH connection to HIVE hypervisor on $HIVE_WAN_SSH_PORT"
  ssh $HIVE_USER@$HIVE_IP -p $HIVE_WAN_SSH_PORT
}


function hive_x11 {
  ssh -X -p $HIVE_WAN_SSH_PORT $HIVE_USER@$HIVE_IP
}

function vmssh {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  echo "Connecting to $VM_USER@$VM_HOST:$VM_PORT"
  ssh -p $VM_PORT $VM_USER@$VM_HOST
}

function vmconsole {
  VM_REMOTE_CMD='cd /opt/ScribbeoServer && RACK_ENV=production racksh'
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  echo "Connecting to $VM_USER@$VM_HOST:$VM_PORT"
  ssh -t -p $VM_PORT $VM_USER@$VM_HOST $VM_REMOTE_CMD
}

function vmscp {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  VM_SEND_FILE=$2
  echo "Sending $VM_SEND_FILE to $VM_USER@$VM_HOST:$VM_PORT:$VM_SEND_FILE"
  scp -P $VM_PORT $VM_SEND_FILE $VM_USER@$VM_HOST:~/$VM_SEND_FILE
}

function vmscp-data {
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  VM_SEND_FILE=$2
  echo "Sending $VM_SEND_FILE to $VM_USER@$VM_HOST:$VM_PORT:$VM_SEND_FILE"
  scp -P $VM_PORT $VM_SEND_FILE $VM_USER@$VM_HOST:/home/curator/media/$VM_SEND_FILE
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
  echo "Updating source code & redeploying on VM $1"
  ssh -t -p $VM_PORT $VM_USER@$VM_HOST $VM_REMOTE_CMD
  echo "Redeploy is complete!"
}

function vmipaversion {
  VM_REMOTE_CMD="cd /opt/ScribbeoServer && script/ipaversion $2"
  VM_PORT=`ruby -e "puts '$1'.to_i+52200"`
  ssh -t -p $VM_PORT $VM_USER@$VM_HOST $VM_REMOTE_CMD
}
