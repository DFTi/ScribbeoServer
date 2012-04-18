class Upload < ActiveRecord::Base
  VERSION = '1.1'

  belongs_to :user
  validates :filename, :presence => true, :uniqueness => true

  before_create do |r|
    r.version = VERSION
  end
  def self.all_of_type(typename)
    where(:content_type=>typename).all
  end
end