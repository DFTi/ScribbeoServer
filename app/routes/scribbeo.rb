class App < Sinatra::Base

  # Implements the old (Scribbeo) API
  # + awareness of user etc.

  get '/list*' do
    # authorize_user!
    # user = User.new.with_password(params[:user])
    # json({
    #   "success"=>user.save,
    #   "errors"=>errors_for(user),
    #   "html"=>partial(:user, :user=>user)
    # })
    json({
      "splat"=>params[:splat]
    })
  end





end
