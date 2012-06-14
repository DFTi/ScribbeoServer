source :rubygems

group :application do

  gem 'sinatra'
  gem 'sinatra-contrib'
  gem 'activerecord', :require => 'active_record'
  gem 'bcrypt-ruby', :require => 'bcrypt'
  gem 'json'
  gem 'warden'
  gem 'launchy'
  gem 'puma'
  gem 'rack-ssl'

  if RUBY_PLATFORM == "java"
    gem 'jruby-rack'
    gem 'jruby-openssl'
    gem 'activerecord-jdbcsqlite3-adapter'
  else
    group :warbler_ignore do
      gem 'dnssd'
      gem 'sqlite3'
    end
  end
end

group :development do
  gem 'pry'
  gem 'racksh'
  gem "warbler"
  gem 'sass'
end

