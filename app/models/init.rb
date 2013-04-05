def db_connect
  if defined? POSTGRES
    ActiveRecord::Base.establish_connection(
      :adapter  => "postgresql",
      :host     => "localhost",
      :username => "scribbeo",
      :password => "KM492hsbA",
      :database => "scribbeo"
    )
  else
    ActiveRecord::Base.establish_connection({
      :adapter => (RUBY_PLATFORM == "java" ? 'jdbcsqlite3' : 'sqlite3'),
      :database => (DEVELOPMENT ? 'db/development.sqlite3' : 'db/production.sqlite3')
    })
  end
end

db_connect

require_relative 'settings'
require_relative 'user'
require_relative 'folder'
require_relative 'upload'
require_relative 'device'
require_relative 'build'