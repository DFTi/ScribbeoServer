source :gemcutter

group :application do
  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    gem 'sqlite3'
  end
  # gem 'ahoy'
  gem 'json'
  gem 'sinatra'
  gem 'warden'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'activerecord', :require => 'active_record'
  gem 'launchy'
end

group :development do
  if RUBY_PLATFORM == "java"
    gem 'trinidad'
  else
    gem 'thin'
  end
  gem 'sinatra-contrib'
  gem 'sass'
  gem 'sprockets'
end
