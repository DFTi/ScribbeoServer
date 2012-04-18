source :rubygems

group :application do

  gem 'sinatra'
  gem 'sinatra-contrib'
  gem 'activerecord', :require => 'active_record'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'json'
  gem 'warden'
  gem 'launchy'


  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    gem 'dnssd'
    gem 'sqlite3'
    gem 'unicorn'
  end
end

group :development do
  if RUBY_PLATFORM == "java"
    gem 'mizuno'
  end
  gem 'racksh'
  gem "warbler"
  gem 'sass'
end