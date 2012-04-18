class CreateUsers < ActiveRecord::Migration
  def self.up
    create_table :users do |t|
      t.string :username
      t.boolean :admin
      t.string :password_hash
      t.string :password_salt
    end

    add_index :users, :username, :uniq => true

  end

  def self.down
    drop_table :users
  end
end
