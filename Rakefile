require './init'
require './db/seed'

namespace :db do
  desc "Migrate the database through scripts in db/migrate."
  task :migrate do
    db_connect
    ActiveRecord::Migrator.migrate(File.join("db","migrate"))
    puts "Seeding..."
    db_seed
  end
end

task :ip do
  data = User.all.map{|u| {u.username=>u.ip_addresses.map(&:address)}}
  ap data, index:false
end