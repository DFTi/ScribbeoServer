class App < Sinatra::Base
  # Description
  # ===========
  # Implements the legacy (Scribbeo) API
  # Extends it with user/folder stuff
  # Stores monolith note archive in the DB

  # Notes regarding database & filesystem
  # =====================================
  # Should actually just stay synchronized with the filesystem,
  # detecting & saving changes to the database. This way,
  # e.g. when timecode is generated, or a note is created,
  # we can associate that new metadata with the db entry.
  # It will also reduce filesystem burden & hasten response.
  # We'll save this stuff for Cruzzeo's API implementation.

  helpers do
    def entry_hash_for(type, entry, relpath)
      out = { 'name'=>entry }
      if type == :file
        if (ext = File.extname(entry)[1..-1]).nil?
          raise "File without extension" # dont send any junk!
        end
        out['ext'] = ext
        out['asset_url'] = File.join("", "asset", relpath, entry)
        out['live_transcode'] = "Not implemented" # TODO this.
      elsif type == :folder
        out['list_url'] = File.join("", "list", relpath, entry)
      end
      out
    end

    def path_from_splat(splat)
      begin
        relpath = splat[0]
        path_parts = relpath.split('/').compact.reject(&:blank?)
        virtual_folder_id = path_parts.delete_at(0)
        virtual_folder = user.folders.find(virtual_folder_id)
      rescue
        return nil
      end
      return File.join(virtual_folder.path, path_parts)
    end
  end

  get '/list*' do
    # authorize_user!

    user = User.find_by_username("keyvan")

    relpath = params[:splat][0]
    res = {"files"=>[], "folders"=>[]}
    # res['debug'] = {'relpath'=>relpath}
    if base_url?(relpath)
      # send all virtual folders
      user.existent_folders.each do |f|
        res['folders'] << {
          "name" => f.name,
          "list_url" => File.join('', 'list', f.id.to_s)
        }
      end
    else
      # need to send REAL files and folders now.
      path_parts = relpath.split('/').compact.reject(&:blank?)

      virtual_folder_id = Folder.find_by_name(path_parts.delete_at(0)).id

      # res['debug']['path_parts'] = path_parts
      # res['debug']['virtual_folder_id'] = virtual_folder_id
      virtual_folder = user.folders.find(virtual_folder_id)
      virtual_folder.entries(path_parts).each do |entry|
        if virtual_folder.has_folder?(entry)
          res["folders"] << entry_hash_for(:folder, entry, relpath)
        else
          res["files"] << entry_hash_for(:file, entry, relpath) rescue next
        end
      end
    end
    json(res)
  end

  get '/asset*' do
    authorize_user!

    asset_path = path_from_splat(params[:splat])
    if asset_path && File.exists?(asset_path)
      send_file(asset_path)
    else
      status 404
    end
  end

  get '/timecode*' do
    authorize_user!

    asset_path = path_from_splat(params[:splat])

    # FIXME Move FFMBC / Timecode stuff into module(s)
    zeros = '00:00:00:00'    
    if asset_path && File.exists?(asset_path)
      # FIXME Should perform caching in larger systems
      details = Open3.popen3("#{Settings.ffmbc_path} -i '#{asset_path}'"){|i,o,e,t| p e.read.chomp }
      
      matches = details.match(/timecode: \d{2}:\d{2}:\d{2}:\d{2}/) # NDFTC
      if matches.nil?
        matches = details.match(/timecode: \d{2}:\d{2}:\d{2};\d{2}/) # DFTC
        matches.nil? ? zeros : matches[0][10..-1].gsub(';', ':') # TODO make client support DFTC notation
      else
        matches[0][10..-1]
      end
    else
      # Log the fact that we failed to get the asset path
      zeros
    end
  end

  get '/notes*' do
    notes = Upload.find_by_content_type("scribbeo/notes/archive")
    # Send an array with the relative URLs, like this:
    # ["/note/+asset+Cuts+311 DC02 111011.mov.AAA", "/note/+asset+Cuts+311 DC02 111011.mov.WAX"]
  end

# -- 

# FIXME I am not happy with how un-DRY the POSTs are
# FIXME set up a before filter to authorize_user! on all these routes

  get '/note/:name' do
    # need this? content_type = 'application/x-binary'
  end

  post '/note/:name' do

  end

  get '/email/:name' do

  end

  post '/email/:name' do
    upload = user.uploads.new do |u|
      u.filename = params[:name]
      u.content_type = "scribbeo/notes/html"
      u.binary_data = request.body.read
    end
    json :success => upload.save
  end

# --

  get '/audio/:name' do
  
  end
  
  post '/audio/:name' do
    upload = user.uploads.find_by_filename(params[:name])
    if upload.nil?
      upload = user.uploads.new
      upload.filename = params[:name]
      upload.content_type = "scribbeo/notes/audio"
    end
    upload.binary_data = request.body.read
    json :success => upload.save
  end

# --

  get '/avid/:name' do

  end
  
  post '/avid/:name' do
    upload = user.uploads.new do |u|
      u.filename = params[:name]
      u.content_type = "scribbeo/markers/avid"
      u.binary_data = request.body.read
    end
    json :success => upload.save
  end
  
# --

  get '/xml/:name' do

  end
  
  post '/xml/:name' do
    upload = user.uploads.new do |u|
      u.filename = params[:name]
      u.content_type = "scribbeo/markers/xml"
      u.binary_data = request.body.read
    end
    json :success => upload.save
  end

end
