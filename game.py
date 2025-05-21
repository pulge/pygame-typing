import pygame as pg
import colors as c
import random
from textbox import TextBox
from wordtarget import WordTarget
from leaderboard import Leaderboard
import os

class Game:
    def __init__(self, game: str='python', debug: bool=False):
        pg.init()
        pg.font.init()
        pg.mixer.init()

        pg.display.set_caption('Typing Game')
        icon = pg.image.load(os.path.join('assets', 'img', 'logo32.png'))
        pg.display.set_icon(icon)

        self.WIDTH, self.HEIGHT = 800, 600
        self.WIN = None
        self.FPS = 60
        self.CLOCK = pg.time.Clock()

        font_path = os.path.join('assets', 'font', 'PressStart2P-Regular.ttf')
        self.FONT = pg.font.Font(font_path, 14)
        self.FONT_BIG = pg.font.Font(font_path, 50)

        self.GUI_SIZE = 100
        self.GUI_BACK = pg.Rect(0, self.HEIGHT - self.GUI_SIZE, self.WIDTH, self.GUI_SIZE)

        self.CORRECT_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'correct.wav'))
        self.CORRECT_SOUND.set_volume(0.1)
        self.HURT_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'hurt1.wav'))
        self.DEATH_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'death.wav'))
        self.LEVELUP_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'levelup.wav'))
        self.LEVELUP_SOUND.set_volume(0.1)
        self.GAMEOVER_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'gameover.mp3'))

        self.word_list = []
        self.filename = game
        with open(os.path.join('word_lists', self.filename + '.txt'), 'r') as file:
            self.word_list = [line.strip() for line in file]

        self.TITLE = self.FONT.render(self.filename, 1, c.WHITE)

        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.score_req = ((self.level + 1) ** 3) * 4 // 5
        self.hits = 0
        self.char_hits = 0
        self.misses = 0
        self.WPM = 0
        self.score_final = 0
        self.words = []
        self.used_lines = []
        self.used_lines_max = 5
        self.debug = False
        self.running = True
        self.on_leaderboard = False
        self.current_time = 0
        self.target_time = 0
        self.target_interval = 2000

        self.txt_input = TextBox(10, self.HEIGHT - 90, 200)
        self.lb = Leaderboard(self.WIDTH // 2 - 200, 20, 400, 400, self.filename, True)
        self.menu_requested = False
        self.BACK_SOUND = pg.mixer.Sound(os.path.join('assets', 'sfx', 'back0.mp3'))
        self.BACK_SOUND.set_volume(0.1)
        self.BACK_SOUND_LOOPS = 1

    def show_main_menu(self):
        self.WIN = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        title = self.FONT_BIG.render("TYPING GAME", True, c.WHITE)
        start_msg = self.FONT.render("Press ENTER to Start", True, c.ORANGE)
        quit_msg = self.FONT.render("Press ESC to Quit", True, c.RED)
  
        while True:
            self.WIN.fill(c.BLACK)
            self.WIN.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 150))
            self.WIN.blit(start_msg, (self.WIDTH // 2 - start_msg.get_width() // 2, 300))
            self.WIN.blit(quit_msg, (self.WIDTH // 2 - quit_msg.get_width() // 2, 350))
            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        return
                    elif event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()

    def draw(self):
        self.WIN.fill(c.BLACK)
        pg.draw.rect(self.WIN, c.DARK_BLUE, self.GUI_BACK)

        self.WIN.blit(self.TITLE, (10, 10))
        self.WIN.blit(self.FONT.render(f'Score: {self.score}', 1, c.WHITE), (10, self.HEIGHT - 50))
        self.WIN.blit(self.FONT.render(f'HI-Score: {self.score_req}', 1, c.ORANGE), (10, self.HEIGHT - 28))
        self.WIN.blit(self.FONT.render(f'Lives: {self.lives}', 1, c.WHITE), (250, self.HEIGHT - 50))
        self.WIN.blit(self.FONT.render(f'Level: {self.level}', 1, c.WHITE), (250, self.HEIGHT - 85))
        self.WIN.blit(self.FONT.render(f'WPM: {self.WPM}', 1, c.WHITE), (500, self.HEIGHT - 85))
        accuracy = 100 if self.misses == 0 else round((self.hits - self.misses) / (self.hits + self.misses) * 100, 1)
        self.WIN.blit(self.FONT.render(f'Accuracy: {accuracy}%', 1, c.WHITE), (500, self.HEIGHT - 50))

        self.txt_input.draw(self.WIN)

        for word in self.words:
            word.move()
            word.draw(self.WIN)

        pg.draw.line(self.WIN, c.RED, (0, self.HEIGHT - self.GUI_SIZE - 10), (self.WIDTH, self.HEIGHT - self.GUI_SIZE - 10), 10)
        pg.display.flip()

    def create_word(self):
        word_text = random.choice(self.word_list)
        font_surface = self.FONT.render(word_text, True, c.GREEN)
        word_width = font_surface.get_width()
        max_x = self.WIDTH - word_width
        x = random.randint(0, max_x)
        while any(abs(x - prev) < 100 for prev in self.used_lines):
            x = random.randint(0, max_x)
        if len(self.used_lines) >= self.used_lines_max:
            self.used_lines.pop(0)
        self.used_lines.append(x)
        self.words.append(WordTarget(word_text, x, 0, self.level))
        self.target_time = self.current_time + random.randint(self.target_interval - 100, self.target_interval + 100)

    def validate_words(self):
        for word in self.words:
            if self.txt_input.returned == word.text:
                self.hits += 1
                self.char_hits += len(word.text)
                self.txt_input.returned = ''
                self.score += len(word.text) * 2
                if self.score >= self.score_req:
                    self.levelup()
                self.CORRECT_SOUND.play()
                self.words.remove(word)
                self.create_word()
                return
        self.misses += 1

    def check_words(self):
        for word in self.words:
            if word.y > self.HEIGHT - self.GUI_SIZE - 30:
                self.lives -= 1
                if self.lives == 0:
                    self.game_over()
                self.HURT_SOUND.play()
                self.words.remove(word)
                return

    def levelup(self):
        self.LEVELUP_SOUND.play()
        self.target_interval = int(self.target_interval * 0.99)
        self.level += 1
        self.score_req = ((self.level + 1) ** 3) * 4 // 5 + self.score_req // 2
        if self.level % 3 == 0:
            self.lives += 1

    def game_over(self):
        text = self.FONT_BIG.render('GAME OVER!', 1, c.WHITE)
        self.WIN.blit(text, (self.WIDTH / 2 - text.get_width() / 2, self.HEIGHT / 2 - text.get_height() / 2))
        self.DEATH_SOUND.play()
        pg.display.update()
        pg.time.delay(2000)
        self.on_leaderboard = True

    def show_leaderboard(self):
        fallback = round((self.hits - self.misses) / (self.hits + self.misses), 2) if (self.hits + self.misses) != 0 else 0
        if self.lb.new_entry:
            self.lb.draw_textbox(self.WIN, self.score, fallback)
            self.lb.update_textbox(self.WIN)
        else:
            self.lb.__init__(self.WIDTH // 2 - 200, 20, 400, 400, self.filename, False)
            self.lb.draw(self.WIN)
            instruction = self.FONT.render("[M] Main Menu  [R] Restart", True, c.GRAY)
            self.WIN.blit(instruction, (self.WIDTH // 2 - instruction.get_width() // 2, self.HEIGHT - 100))
        pg.display.update()

    def calculate_wpm(self):
        return int((self.char_hits / 5) / ((self.current_time / 60000)))

    def start(self):
        self.WIN = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.show_main_menu()
        self.create_word()
        self.BACK_SOUND.play()

        while self.running:
            stop_sound = True
            while self.on_leaderboard:
                self.score_final = 0 if (self.hits + self.misses) == 0 else int(self.score * round((self.hits - self.misses) / (self.hits + self.misses), 2))
                if stop_sound:
                    pg.mixer.stop()
                    self.GAMEOVER_SOUND.play()
                    stop_sound = False
                self.CLOCK.tick(self.FPS)

                for event in pg.event.get():
                    self.lb.txtbox.handle_event(event)
                    if event.type == pg.QUIT:
                        self.running = False
                        self.on_leaderboard = False
                    elif event.type == pg.KEYDOWN:
                        if self.lb.new_entry:
                            if event.key == pg.K_RETURN:
                                self.lb.save_score(self.lb.txtbox.returned, self.score_final)
                                self.lb.new_entry = False
                        else:
                            if event.key == pg.K_m:
                                self.on_leaderboard = False
                                self.GAMEOVER_SOUND.stop()
                                self.reset_game()
                                self.show_main_menu()
                                self.create_word()
                                self.BACK_SOUND.play()
                            elif event.key == pg.K_r:
                                self.on_leaderboard = False
                                self.GAMEOVER_SOUND.stop()
                                self.reset_game()
                                self.create_word()
                                self.BACK_SOUND.play()
                self.show_leaderboard()

            self.CLOCK.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                self.txt_input.handle_event(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.validate_words()
                        self.WPM = self.calculate_wpm()
            self.current_time = pg.time.get_ticks()
            if self.current_time >= self.target_time:
                self.create_word()
            if self.current_time > ((self.BACK_SOUND.get_length() * 1000) * self.BACK_SOUND_LOOPS) + 1000:
                self.BACK_SOUND.play()
                self.BACK_SOUND_LOOPS += 1
            self.check_words()
            self.draw()
        pg.quit()