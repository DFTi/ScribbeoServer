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
  end

  get '/list*' do
    authorize_user!
    relpath = params[:splat][0]
    res = {"files"=>[], "folders"=>[]}
    # res['debug'] = {'relpath'=>relpath}
    if base_url?(relpath)
      # send all virtual folders
      user.existent_folders.each do |f|
        res[:folders] = {
          "name" => f.name,
          "list_url" => File.join('', 'list', f.id.to_s)
        }
      end
    else
      # need to send REAL files and folders now.
      path_parts = relpath.split('/').compact.reject(&:blank?)
      virtual_folder_id = path_parts.delete_at(0)
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
    json(res) # like a boss
  end

  get '/asset*' do
    #authorize_user!
    user = User.find_by_username "Keyvan"

    relpath = params[:splat][0]
    path_parts = relpath.split('/').compact.reject(&:blank?)
    virtual_folder_id = path_parts.delete_at(0)
    virtual_folder = user.folders.find(virtual_folder_id)
    asset_path = File.join(virtual_folder.path, path_parts)
    if File.exists? asset_path
      send_file(asset_path, {
        :stream=>true,
        :type=>'video/quicktime',
        :disposition=>nil
      })
    else
      status 404
    end
  end

end
