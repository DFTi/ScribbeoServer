class User < ActiveRecord::Base
  has_many :uploads
  has_many :note_archive_files
  has_and_belongs_to_many :folders
  
  attr_accessible :username, :password, :password_confirmation
  attr_accessor :password
  before_save :encrypt_password

  validates :password, :confirmation=>true
  validates :password, :presence=>true, :on=>:create
  validates :username, :presence=>true, :uniqueness => {:case_sensitive => false}
  
  before_destroy { folders.clear }
  
  def encrypt_password
    if password.present?
      self.password_salt = BCrypt::Engine.generate_salt
      self.password_hash = BCrypt::Engine.hash_secret(password, password_salt)
    end
  end
  
  def with_password(params)
    self.username = params[:username] if params[:username]
    self.password = params[:password]
    self.password_confirmation = params[:confirmation]
    self
  end
  
  # params = {
  #   "user":{
  #     "old_password":"...",
  #     "password":"...",
  #     "confirmation":"..."
  #   }
  # }
  def change_password(params)
    out = {"success"=>false}
    if params[:password] != params[:confirmation]
      return out[:errors] = "Password does not match confirmation!"
    end
    if User.authenticate(self.username, params[:old_password])
      out[:success] = self.with_password(params).save
      out[:errors] = self.errors.full_messages
      out[:notice] = " The password for #{self.username} has been updated."
    else
      out[:errors] = "Current password was incorrect."
    end
  end
  
  def self.authenticate(username, password)
    user = where(["lower(username) = ?", username.downcase]).first
    if user && user.password_hash == BCrypt::Engine.hash_secret(password, user.password_salt)
      user
    else
      nil
    end
  end
  
  def admin?
    !!self.admin
  end

  def self.all_but_admin
    all.reject {|u| u.username=="admin"}
  end

  def existent_folders
    folders.reject { |f| !File.directory?(f.path) }
  end

end