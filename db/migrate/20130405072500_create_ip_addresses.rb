class CreateIpAddresses < ActiveRecord::Migration
  def change
    create_table :ip_addresses do |t|
      t.string :address
      t.integer :user_id

      t.timestamps
    end
  end
end