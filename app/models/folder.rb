class Folder < ActiveRecord::Base
  class FolderValidator < ActiveModel::Validator
    def validate(record)
      unless File.directory? record.path
        record.errors[:path] << "does not actually exist on filesystem."
      end
    end
  end
  has_and_belongs_to_many :users
  validates :name, :uniqueness=>true, :presence=>true
  validates :path, :uniqueness=>true, :presence=>true
  include ActiveModel::Validations
  #validates_with FolderValidator
  before_destroy { users.clear }

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

  def exists?
    Dir.exists? path
  end

  def entries(path_parts = nil)
    dir_path = path_parts.nil? ? path : File.join(path, path_parts)
    Dir.entries(dir_path).reject do |entry|
      ['..','.','Thumbs.db','.DS_Store'].include? entry
    end
  end

  def has_folder?(entry)
    File.directory?(File.join("", path, entry))
  end

end