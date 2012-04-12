DEVELOPMENT = true
require 'rubygems'
require 'bundler/setup'
Bundler.require(:application)

if DEVELOPMENT
  Bundler.require(:development)
  require 'sinatra/base'
  require 'sinatra/reloader'
end


require './lib/bonjour'
require './lib/auth'
require 'sinatra/json'
require 'sinatra/namespace'
require './app/app'


if RUBY_PLATFORM == "java"
  require './lib/tray_application'
  class App
    Bonjour = Bonjour.new(Settings.instance_name, Settings.instance_port)
  end
end
