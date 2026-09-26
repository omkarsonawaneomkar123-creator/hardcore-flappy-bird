import random
import math
import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label

# Mobile Portrait Screen Aspect Ratio (400x600 equivalent)
Window.size = (400, 600)

class HardcoreFlappyGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. High Score Load
        self.high_score_file = "highscore.txt"
        self.high_score = self.load_high_score()

        # 2. Game Variables & Physics (Kivy Y-axis goes UP)
        self.bird_x = 80
        self.bird_y = 300
        self.bird_speed_y = 0
        self.gravity = -0.55
        
        self.pipe_x = 400
        self.pipe_width = 60
        self.pipe_height = random.randint(100, 300)
        self.pipe_gap = random.randint(120, 180)
        self.pipe_move_dir = 1
        
        self.score = 0
        self.game_over = False
        
        self.size_timer = 0
        self.bird_radius = 17

        # 3. UI Overlay Labels
        self.score_label = Label(text="Score: 0", pos=(20, 540), font_size='18sp', bold=True, color=(1, 1, 1, 1))
        self.high_score_label = Label(text=f"High: {self.high_score}", pos=(270, 540), font_size='18sp', bold=True, color=(1, 1, 1, 1))
        self.game_over_label = Label(text="", pos=(100, 300), font_size='22sp', bold=True, color=(1, 0, 0, 1))
        
        self.add_widget(self.score_label)
        self.add_widget(self.high_score_label)
        self.add_widget(self.game_over_label)
        
        # Schedule 60 FPS Main Loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def load_high_score(self):
        if os.path.exists(self.high_score_file):
            try:
                with open(self.high_score_file, "r") as f:
                    return int(f.read().strip())
            except ValueError:
                return 0
        return 0

    def save_high_score(self, val):
        with open(self.high_score_file, "w") as f:
            f.write(str(val))

    def on_touch_down(self, touch):
        # Screen par kahin bhi tap karne par Jump / Restart hoga
        if self.game_over:
            self.reset_game()
        else:
            self.bird_speed_y = 8.5

    def reset_game(self):
        self.bird_y = 300
        self.bird_speed_y = 0
        self.pipe_x = self.width if self.width > 0 else 400
        self.pipe_width = 60
        self.pipe_gap = random.randint(120, 180)
        self.pipe_height = random.randint(100, 300)
        self.pipe_move_dir = 1
        self.score = 0
        self.size_timer = 0
        self.game_over = False
        self.game_over_label.text = ""
        self.score_label.text = f"Score: {self.score}"

    def update(self, dt):
        if self.game_over:
            return

        # --- PHYSICS & LOGIC ---
        self.bird_speed_y += self.gravity
        self.bird_y += self.bird_speed_y

        # Bird Size Pulsating Logic
        self.size_timer += (2 * math.pi) / 150
        self.bird_radius = int(17 + math.sin(self.size_timer) * 7)

        # Dynamic Speed & Dynamic Width Logic
        current_pipe_speed = 4 + (self.score // 5)
        width_level = (self.score // 4) % 3
        if width_level == 1:
            self.pipe_width = 40
        elif width_level == 2:
            self.pipe_width = 80
        else:
            self.pipe_width = 60

        # Pipe Horizontal Movement
        self.pipe_x -= current_pipe_speed

        # Oscillating Moving Pipes (Score >= 7)
        if self.score >= 7:
            self.pipe_height += self.pipe_move_dir * 2
            if self.pipe_height <= 80 or self.pipe_height >= 320:
                self.pipe_move_dir *= -1

        # Pipe Respawn & Score System
        if self.pipe_x < -self.pipe_width:
            self.pipe_x = self.width if self.width > 0 else 400
            self.pipe_gap = random.randint(120, 180)
            self.pipe_height = random.randint(100, 300)
            self.score += 1
            self.score_label.text = f"Score: {self.score}"

            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score(self.high_score)
                self.high_score_label.text = f"High: {self.high_score}"

        # Collision Check Logic
        bottom_pipe_top = self.pipe_height
        top_pipe_bottom = self.pipe_height + self.pipe_gap

        if (self.bird_y - self.bird_radius <= 0 or 
            self.bird_y + self.bird_radius >= self.height or
            (self.pipe_x <= self.bird_x + self.bird_radius and self.bird_x - self.bird_radius <= self.pipe_x + self.pipe_width and
             (self.bird_y - self.bird_radius <= bottom_pipe_top or self.bird_y + self.bird_radius >= top_pipe_bottom))):
            self.game_over = True
            self.game_over_label.text = "GAME OVER\nTap to Play Again"

        # --- GRAPHICS RENDERING (OPENGL ACCELERATED) ---
        self.canvas.clear()
        with self.canvas:
            # 1. Day / Night Cycle Background
            is_night = (self.score // 10) % 2 == 1
            if is_night:
                Color(0.05, 0.08, 0.2, 1)  # Dark Blue
            else:
                Color(0.53, 0.81, 0.92, 1) # Sky Blue
            Rectangle(pos=(0, 0), size=self.size)

            # 2. Dynamic Pipe Colors (Score Thresholds 5, 10, 15)
            if self.score >= 15:
                Color(0.8, 0.1, 0.1, 1)    # Red
            elif self.score >= 10:
                Color(0.5, 0.0, 0.5, 1)    # Purple
            elif self.score >= 5:
                Color(1.0, 0.55, 0.0, 1)   # Orange
            else:
                Color(0.13, 0.55, 0.13, 1) # Green

            # Bottom Pipe
            Rectangle(pos=(self.pipe_x, 0), size=(self.pipe_width, self.pipe_height))
            # Top Pipe
            Rectangle(pos=(self.pipe_x, top_pipe_bottom), size=(self.pipe_width, max(0, self.height - top_pipe_bottom)))

            # 3. Dynamic Pulsating Bird
            Color(1, 0.85, 0, 1) # Yellow Bird
            Ellipse(pos=(self.bird_x - self.bird_radius, self.bird_y - self.bird_radius),
                    size=(self.bird_radius * 2, self.bird_radius * 2))


class FlappyApp(App):
    def build(self):
        return HardcoreFlappyGame()

if __name__ == '__main__':
    FlappyApp().run()
