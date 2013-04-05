class User < ActiveRecord::Base
  has_many :uploads
  has_many :note_archive_files
  has_many :ip_addresses
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

  def set_password!(new_password)
    self.with_password({:password => password}).save!
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

  def track request
    remote_ip = request.env['HTTP_X_FORWARDED_FOR'] || request.env['REMOTE_ADDR']
    remote_ip = remote_ip.scan(/[\d.]+/).first
    self.ip_addresses.find_or_create_by_address remote_ip
  end
end