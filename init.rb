require 'rubygems'
require 'bundler/setup'
Bundler.require(:application)
DEVELOPMENT = (ENV['RACK_ENV'] == 'development')
PRODUCTION = DEVELOPMENT ? false : true
puts "Env: #{PRODUCTION ? 'production' : 'development'}"

if DEVELOPMENT
  Bundler.require(:development)
  require 'sinatra/base'
  require 'sinatra/reloader'
end

if PRODUCTION
  PG_CONNECTION_SETTINGS = {
      :adapter  => "postgresql",
      :host     => "localhost",
      :username => "scribbeo",
      :password => "KM492hsbA",
      :database => "scribbeo"    
  }
else
  SQLITE_CONNECTION_SETTINGS = {
    :adapter => (RUBY_PLATFORM == "java" ? 'jdbcsqlite3' : 'sqlite3'),
    :database => (DEVELOPMENT ? 'db/development.sqlite3' : 'db/production.sqlite3')
  }
end

require 'fileutils'
require 'open3'
require 'socket'
require 'timeout'

require './lib/auth'
require 'sinatra/json'
require 'sinatra/namespace'
require './app/app'