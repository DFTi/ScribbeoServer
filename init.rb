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

require 'open3'
require 'socket'
require 'timeout'

require './lib/bonjour'
require './lib/auth'
require 'sinatra/json'
require 'sinatra/namespace'
require './app/app'


# SETTINGS = {
#   :name=>"ScribbeoServer",
#   :icon=>'images/ruby.png',
#   :url=>'http://localhost:9292/'
# }

class App
  BONJOUR = Bonjour.new(Settings.instance_name, Settings.instance_port)
  
  if RUBY_PLATFORM == "java"
    require './lib/tray_application'
    TRAY = TrayApplication.new(Settings.instance_name, Settings.icon_path)
    TRAY.item('Settings') do
      Settings.app_url ||= "http://localhost:3000/"
      Launchy.open Settings.app_url # launch on load
    end
    TRAY.item('Shutdown') do
      java.lang.System::exit(0)
    end
    TRAY.run
  end
end

