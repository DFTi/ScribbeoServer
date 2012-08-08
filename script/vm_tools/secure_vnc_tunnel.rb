#!/usr/bin/env ruby

LOCAL_TUNNEL_PORT = ARGV[0]
HOST_IP = ARGV[1]
HOST_LOCAL_TUNNEL_PORT = ARGV[2]
HOST_WAN_SSH_PORT = ARGV[3]
HOST_USER = ARGV[4]

def recently_ran?(secs)
  File.open(__FILE__, "r+") {|f| @timestamp = f.mtime }
  (Time.now - @timestamp) < secs
end
if recently_ran?(5)
  puts "Recently built tunnel and VNC'd, skipping that."
  exit
else
  `touch #{__FILE__}`
  puts "Killing port-stealing stale sessions"
  `ps aux | grep "ssh -L #{LOCAL_TUNNEL_PORT}" | awk '{print $2}'`.split.each do |pid|
    `kill -9 #{pid} > /dev/null 2>&1`
    puts "Killed stale process #{pid}"
  end
  puts "Ports cleared (hopefully). Attempting to create a secure VNC tunnel."
  fork {
    `ssh -L #{LOCAL_TUNNEL_PORT}:localhost:#{HOST_LOCAL_TUNNEL_PORT} -p #{HOST_WAN_SSH_PORT} -N -f -l #{HOST_USER} #{HOST_IP}`  
  }
  puts "Secure VNC tunnel to #{HOST_IP}:#{HOST_LOCAL_TUNNEL_PORT} constructed on localhost:#{LOCAL_TUNNEL_PORT}."
  print "Launching VNC"
  5.times do 
    sleep 1
    print '.'
  end
  puts
  `open vnc://localhost:#{LOCAL_TUNNEL_PORT}`
  puts "VNC launched."
end