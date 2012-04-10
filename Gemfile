source :gemcutter

group :application do
  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    gem 'sqlite3'
  end
  gem 'json'
  gem 'sinatra'
  gem 'warden'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'activerecord', :require => 'active_record'
  gem 'launchy'
end

group :development do
  if RUBY_PLATFORM == "java"
    gem 'trinidad' # Can't stream--find a replacement, possibly jetpack for packaging https://github.com/square/jetpack
  else
    gem 'unicorn'
  end
  gem 'sinatra-contrib'
  gem 'sass'
  gem 'sprockets'
end
