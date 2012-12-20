class App < Sinatra::Base
  get "/" do
    if user && user.admin?
      redirect '/admin/dashboard'
    elsif user
      erb :home
    else
      redirect '/login'
    end
  end

  if DEVELOPMENT
    get '/env' do 
      my_env = {}
      env.each do |k,v|
        v = v.to_s if v.class != String
        my_env[k] = v 
      end
      json(my_env)
    end
  end

  # Permitted user can now do basic management
  namespace "/folder/:id" do
    before do
      authorize_user!
      folder = Folder.find(params[:id])
      throw :halt, [ 401, 'Not authorized' ] if !user.folders.include?(folder)
      @title = "Uploader"
      request.instance_eval { def secure?; true; end } if PRODUCTION
    end
    # Subfolders...
    # They inherit permissions of parent
    post '/subfolder/create' do
      parent = Folder.find(params[:id])
      @folder = parent.folders.new
      @folder.add_user(user)
      @folder.path = File.join(parent.root_relative_path, params[:subfolder])
      @folder.name = params[:subfolder]
      redirect "folder/#{(@folder.save ? @folder : parent).id}/contents"
    end

    get '/contents' do
      @folder = Folder.find(params[:id])
      if @folder && @folder.exists?
        erb(:folder_contents)
      else
        "Folder does not exist on the filesystem"
      end
    end

    # Delete files through web interface
    post '/contents/:filename/delete' do
      folder = Folder.find(params[:id])
      res = File.basename(FileUtils.rm(File.join(folder.path, params[:filename]))[0]) rescue false
      json({
        "success"=>res ? true : false,
        "filename"=>params[:filename],
        "file_deletion"=>true
      })
    end

    post '/upload' do
      unless params[:file] &&
        (tmpfile = params[:file][:tempfile]) &&
        (name = params[:file][:filename])
        @error = "No file selected"
        return "No file selected"
      end
      @folder = Folder.find(params[:id])
      STDERR.puts "Uploading file, original name #{name.inspect}"
      path = File.join(@folder.path, name)
      File.open(path, "w") do |f|
        while blk = tmpfile.read(65536)
          f.write(blk)
        end
      end
      tmpfile.close!
      @notice="Uploaded!"
      erb(:folder_contents)
    end
  end

end
