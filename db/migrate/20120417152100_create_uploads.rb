class CreateUploads < ActiveRecord::Migration
  def self.up
    create_table :uploads do |t|
      t.integer :user_id
      t.string :filename
      t.string :content_type
      t.binary :binary_data
      t.string :version
      t.timestamps
    end
    
    add_index :uploads, :filename, :uniq => true

  end

  def self.down
    drop_table :uploads
  end
end