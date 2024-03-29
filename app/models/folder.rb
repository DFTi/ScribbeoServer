class Folder < ActiveRecord::Base
  has_and_belongs_to_many :users
  has_many :folders
  belongs_to :folder

  before_validation { self.path = File.join(Settings.root_directory, self.path) }
  
  before_destroy do
    users.clear
    folders.each {|f| f.destroy }
    FileUtils.rm_rf self.path
  end
  
  class FolderValidator < ActiveModel::Validator
    def validate(record)
      if record.path.split('/').include?('..')
        record.errors[:path] << "is invalid."
      elsif !File.directory?(record.path)
        old_umask = File::umask(0)
        begin
          Dir.mkdir(record.path, 0777)
        rescue
          record.errors[:path] << "could not be created on disk (#{record.path})."
        ensure
          File::umask(old_umask)
        end
      end
    end
  end

  
  include ActiveModel::Validations
  validates :name, :uniqueness=>true, :presence=>true
  validates :path, :uniqueness=>true, :presence=>true
  validates_with FolderValidator
  
  def root
    top = self
    while top.is_a? Folder
      if top.folder.nil?
        return top 
      else
        top = top.folder
      end
    end
    return top
  end

  def add_user(user)
    if self.users.include? user
      {"success"=>false,
       "errors"=>"#{user.username} already has access to #{self.name}"}
    elsif self.users << user
      {"success"=>true,
       "message"=>"#{user.username} can now access #{self.name}"}
    end
  end
  
  def remove_user(user)
    if (self.users.delete(user) ? true : false)
      {"success"=>true, 
       "message"=>"Removed #{user.username}'s access to #{self.name}"}
    else
      {"success"=>false,
       "errors"=>"Failed to remove #{user.username} from #{self.name}"}
    end
  end

  def root_relative_path
    self.path.gsub(Settings.root_directory, '')
  end

  def exists?
    Dir.exists? path
  end

  def entries(path_parts = nil)
    dir_path = path_parts.nil? ? path : File.join(path, path_parts)
    if File.directory? dir_path
      Dir.entries(dir_path).reject do |entry|
        ['..','.','Thumbs.db','.DS_Store'].include? entry
      end
    else
      Array.new # Return an empty array if there are no entries.
    end
  end

  def has_folder?(relpath)
    File.directory?(File.join("", path, relpath))
  end

end