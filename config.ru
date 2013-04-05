require './init'

if DEVELOPMENT
  require 'sass/plugin/rack'
  Sass::Plugin.options[:template_location] = 'app/views/stylesheets'
  Sass::Plugin.options[:css_location] = 'app/public/css'
  use Sass::Plugin::Rack
end

use ActiveRecord::ConnectionAdapters::ConnectionManagement
use Rack::Session::Cookie, :secret => Mac.addr.gsub(':', rand(255).to_s)
use Rack::MethodOverride

use Warden::Manager do |manager|
  manager.default_strategies :password
  manager.failure_app = App
end

map "/" do 
  run App
end
