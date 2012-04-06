class App < Sinatra::Base

  namespace '/admin' do 
    before do
      @title = "Admin"
      authorize_user!
    end
    
    get "/dashboard" do
      @users = User.all_but_admin
      @folders = Folder.all
      erb :admin
    end

    namespace '/user' do
      post '/create' do
        authorize_user!
        user = User.new.with_password(params[:user])
        json({
          "success"=>user.save,
          "errors"=>errors_for(user),
          "html"=>partial(:user, :user=>user)
        })
      end
    
      post '/destroy' do
        json({
          "success"=>(User.destroy(params[:id]) ? true : false),
          "id"=>params[:id]
        })
      end

      put '/change_password' do
        user = User.find(params[:id])
        json({
          "success"=>(user.change_password(params[:user]))
        })
      end
    end
    
    namespace "/folder" do      
      get '/index.html.json' do 
        folders = Folder.all
        json({
          "html"=>partial(:folders, :folders=>folders)
        })
      end

      post '/create' do
        folder = Folder.new(params[:folder])
        json({
          "success"=>folder.save,
          "errors"=>errors_for(folder),
          "html"=>partial(:folder, :folder=>folder)
        })
      end
    
      post '/destroy' do
        json({
          "success"=>(Folder.destroy(params[:id]) ? true : false),
          "id"=>params[:id]
        })
      end
    end
    
    namespace '/permission' do
      post '/set' do
        u = User.find(params[:user_id])
        f = Folder.find(params[:folder_id])
        json(f.add_user(u).merge({
          'html'=>partial(:folder, :folder=>f)
        }))
      end

      post '/unset' do
        u = User.find(params[:id])
        f = Folder.find(params[:folder_id])
        json(f.remove_user(u).merge({
          'count'=>f.users.count,
          'id'=>f.id
        }))
      end
    end


  end

end
