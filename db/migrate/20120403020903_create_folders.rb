class CreateFolders < ActiveRecord::Migration
  def self.up
    create_table :folders do |t|
      t.integer :folder_id
      t.string :name
      t.string :path
    end

    add_index :folders, :name, :uniq => true

  end

  def self.down
    drop_table :folders
  end
end
