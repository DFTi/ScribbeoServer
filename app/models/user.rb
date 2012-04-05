class User < ActiveRecord::Base
  has_and_belongs_to_many :folders
  
  attr_accessible :username, :password, :password_confirmation
  attr_accessor :password
  before_save :encrypt_password
  
  validates_confirmation_of :password
  validates_presence_of :password, :on => :create
  validates_presence_of :username
  validates_uniqueness_of :username
  
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
  #     "current_password":"...",
  #     "password":"...",
  #     "confirmation":"..."
  #   }
  # }
  def change_password(params)
    out = {}
    if User.authenticate(self.username, params[:old_password])
      out[:success] = self.with_password(params).save
      out[:errors] = self.errors.full_messages
    else
      out[:errors] = "Current password was incorrect."
    end
  end
  
  def self.authenticate(username, password)
    user = find_by_username(username)
    if user && user.password_hash == BCrypt::Engine.hash_secret(password, user.password_salt)
      user
    else
      nil
    end
  end
  
  def self.all_but_admin
    all.reject {|u| u.username=="admin"}
  end
end