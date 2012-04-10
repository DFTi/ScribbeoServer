source :gemcutter

group :application do
  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    gem 'sqlite3'
    gem 'unicorn'
  end
  gem 'json'
  gem 'sinatra'
  gem 'sinatra-contrib'
  gem 'activerecord', :require => 'active_record'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'warden'
  gem 'launchy'
end

group :development do
  if RUBY_PLATFORM == "java"
    gem 'mizuno'
  end
  gem 'sass'
  gem 'sprockets'
end