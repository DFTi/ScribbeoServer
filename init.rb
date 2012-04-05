DEVELOPMENT = true
require 'bundler/setup'
Bundler.require(:application)

if DEVELOPMENT
  Bundler.require(:development)
  require 'sinatra/base'
  require 'sinatra/reloader'
end

if RUBY_PLATFORM == "java"
  require './lib/tray_application'
end

# require './lib/bonjour'
require './lib/auth'
require 'sinatra/json'
require 'sinatra/namespace'
require './app/app'

=begin

Todo:

  Bonjour (aka DNSSD, MDNS, ?) <-- give that shit an interface too for superusers
    ^
    ^ Scribbeo client uses the bonjour spec to get a list of servers (it is just dumb-filtering it to match against _videoTree_, but we can just use the existing code to populate a tableview of servers with this paramater configured.)
    
=end