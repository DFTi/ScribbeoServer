class App < Sinatra::Base 

  configure do
    register Sinatra::Reloader if DEVELOPMENT
    register Sinatra::Namespace
  end
  before { @title = "ScribbeoServer"}

end

require_relative 'models/init'
require_relative 'helpers/init'
require_relative 'routes/init'