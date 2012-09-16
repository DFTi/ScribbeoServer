#!/usr/bin/env ruby
LOCAL_TUNNEL_PORT = ARGV[0]

puts "Killing port-stealing ssh sessions on #{LOCAL_TUNNEL_PORT}"

`ps aux | grep "ssh -L #{LOCAL_TUNNEL_PORT}" | awk '{print $2}'`.split.each do |pid|
  `kill -9 #{pid} > /dev/null 2>&1`
end