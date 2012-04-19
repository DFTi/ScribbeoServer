def db_connect
  ActiveRecord::Base.establish_connection({
    :adapter => (RUBY_PLATFORM == "java" ? 'jdbcsqlite3' : 'sqlite3'),
    :database => (DEVELOPMENT ? 'db/development.sqlite3' : 'db/production.sqlite3')
  })
end

db_connect

require_relative 'settings'
require_relative 'user'
require_relative 'folder'
require_relative 'upload'