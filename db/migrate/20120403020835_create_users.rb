class CreateUsers < ActiveRecord::Migration
  def self.up
    create_table :users do |t|
      t.string :username
      t.string :password_hash
      t.string :password_salt
    end

    add_index :users, :username, :uniq => true

    User.create(:username=>"admin", :password=>"admin", :password_confirmation=>"admin")
  end

  def self.down
    drop_table :users
  end
end
