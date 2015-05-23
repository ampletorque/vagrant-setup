require 'gosu'
require './floor'

class GameWindow < Gosu::Window
  def initialize
    super(400, 400, false)
    self.caption = "Render Map"
    @image = Gosu::Image.new(self, "media/one.png", false)
    @image_2 = Gosu::Image.new(self, "media/two.png", false)

    @background_image = Gosu::Image.new(self, "media/Space.png", true)

    @floor = Floor.new({:width => 25, :height => 25})
    @floor.create_boundaries
    @scaler = 15
  end

  def draw
    @floor.map.each_index do |y|
      @floor.map[y].each_index do |x|
        if(@floor.is_solid?(x, y))
          @image.draw(x*@scaler, y*@scaler, 1)
        else
          @image_2.draw(x*@scaler, y*@scaler, 1)
        end
      end
    end
  end

end

window = GameWindow.new
window.show
