def db_connect
  ActiveRecord::Base.establish_connection PRODUCTION ? PG_CONNECTION_SETTINGS : SQLITE_CONNECTION_SETTINGS 
end

db_connect

require_relative 'settings'
require_relative 'user'
require_relative 'ip_address'
require_relative 'folder'
require_relative 'upload'
require_relative 'device'
require_relative 'build'