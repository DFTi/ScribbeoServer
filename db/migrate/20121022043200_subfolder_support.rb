class SubfolderSupport < ActiveRecord::Migration
  def self.up
    change_table :folders do |t|
      t.integer :folder_id
    end
  end

  def self.down
    remove_column :folders, :folder_id
  end
end
