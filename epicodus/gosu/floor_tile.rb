class Floor_tile

  def initialize(window, map)
    @image = Gosu::Image.new(window, "media/Starfighter.bmp", false)
    @x = @y = 10
    @map = map
  end

  def draw
    
    map.each do |sub|
      sub.each do
         @image.draw(@x, @y, 1)
       end
     end

  end

end
