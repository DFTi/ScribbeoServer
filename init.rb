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

require 'fileutils'
require 'open3'
require 'socket'
require 'timeout'

require './lib/auth'
require 'sinatra/json'
require 'sinatra/namespace'
require './app/app'