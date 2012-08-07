class CreateDevices < ActiveRecord::Migration
  def change
    create_table :devices do |t|
      t.string :name
      t.string :udid
      t.string :email

      t.timestamps
    end
  end
end
