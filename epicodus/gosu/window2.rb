require 'gosu'
require './star'
require './player'
require './zorder'

class GameWindow < Gosu::Window
  def initialize
    super(640, 480, false)
    self.caption = "Gosu Tutorial Game"

    @background_image = Gosu::Image.new(self, "media/Space.png", true)

#    @player = Player.new(self)
#    @player.warp(320, 240)

#    @star_anim = Gosu::Image::load_tiles(self, "media/Star.png", 25, 25, false)
#    @stars = Array.new

  end

  def draw
    @background_image.draw(0, 0, ZOrder::Background)
#    @player.draw
#    @stars.each { |star| star.draw }
  end
  
end

window = GameWindow.new
window.show
