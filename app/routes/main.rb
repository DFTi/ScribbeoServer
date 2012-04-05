class App < Sinatra::Base
  get "/" do
    redirect '/admin/dashboard'
  end
end
