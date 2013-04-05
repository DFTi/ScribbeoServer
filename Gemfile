source 'https://rubygems.org'

group :application do

  gem 'sinatra'
  gem 'sinatra-contrib'
  gem 'activerecord', :require => 'active_record'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'json'
  gem 'warden'
  gem 'launchy'
  gem 'rack-ssl'
  gem 'macaddr' # Used to set the cookie secret in rackup

  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    group :warbler_ignore do
      gem 'dnssd'
      gem 'pg'
    end
  end
end

group :development do
  gem 'pry'
  gem 'racksh'
  gem "warbler"
  gem 'sass'
  gem 'sqlite3'
end