require 'gosu'
include Gosu

require_relative 'map'
require_relative 'node'
require_relative 'timer'
require_relative 'floor'

class Life < Window

   def initialize
      super screen_width, screen_height, true
      self.caption = "Map Render"
      # @pause = true
      @map = Map.new(self, 96, 54)
#      @tmr = Timer.new
#      enable_undocumented_retrofication
   end

  #  def needs_cursor?
  #     @pause
  #  end

  #  def button_down(id)
  #     case id
  #     when KbEscape
  #        close
  #     when KbSpace
  #        @pause = !@pause
  #     when MsLeft
  #        @map.clicked(mouse_x, mouse_y, false) if @pause
  #     when KbR
  #        @map.reset
  #     end
  #  end

  #  def update
  #     if !@pause
  #        if @tmr.time > 200
  #           @map.update
  #           @tmr.reset
  #        end
  #     else
  #        if button_down?(MsRight)
  #           @map.clicked(mouse_x, mouse_y, true)
  #        end
  #     end
  #  end

   def draw
      scale(@map.rat_x, @map.rat_y) {
         @Map.draw
      }
   end
end

Life.new.show
