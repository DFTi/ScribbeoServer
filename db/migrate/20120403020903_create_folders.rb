class CreateFolders < ActiveRecord::Migration
  def self.up
    create_table :folders do |t|
      t.string :name
      t.string :path
    end
  end

  def self.down
    drop_table :folders
  end
end
