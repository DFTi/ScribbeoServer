require './init'

namespace :db do
  desc "Migrate the database through scripts in db/migrate."
  task :migrate do
    db_connect
    ActiveRecord::Migrator.migrate("db/migrate/")
  end
end