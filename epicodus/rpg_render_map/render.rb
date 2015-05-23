require 'gosu'
include Gosu

require_relative 'floor'

class Render < Window

  def initialize
     super screen_width, screen_height, true
     self.caption = "Map Render"
     @test_floor = Floor.new({:width => 10, :height => 10})

    #  @win = window
    #  @w, @h = width, height
    #  @rat_x, @rat_y = window.width.fdiv(@w), window.height.fdiv(@h)
    @w = 10
    @h = 10
    @map = Array.new(@w) { Array.new(@h) }
   end

       def paint
  #          @img = self.record(@w, @h) {
               @map.each do |row|
                   row.each do |n|
                       n.draw
                   end
               end
    #        }
       end

       def draw
          # scale(@map.rat_x, @map.rat_y) {
            #  @Map.draw
      #     }
      #  end
         window.draw
#          window.draw_quad(@x, )
#         window.draw_quad(@x, World::HEIGHT - 20, WHITE, @x + @width, World::HEIGHT - 20, WHITE, @x + @width, World::HEIGHT - 5, WHITE, @x, World::HEIGHT - 5, WHITE)
       end

      #  def draw(camera_x,camera_y)
		  #     for x in ((camera_x/32) - 1).to_i .. ((camera_x/32) + 30).to_i
		  #     	for y in ((camera_y/32) - 1).to_i .. ((camera_y/32) + 19).to_i
			#     	  if(x < @width) && (y < @height)
			# 		    tile = @tiles[x][y]
			# 		    @tileset[tile].draw(x * 32, y * 32, 0)
			# 	      end
			#       end
		  #     end
	    #  end

 end

Render.new.show
