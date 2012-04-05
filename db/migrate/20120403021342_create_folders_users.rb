class CreateFoldersUsers < ActiveRecord::Migration
  def self.up
    create_table :folders_users do |t|
      t.integer :folder_id
      t.integer :user_id
    end
  end

  def self.down
    drop_table :folders_users
  end
end
