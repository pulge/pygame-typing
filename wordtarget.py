import pygame as pg
import colors as c
import os

class WordTarget:
	def __init__(self, text: str, x: int, y: int, level: int):
		font_path = os.path.join('assets', 'font', 'PressStart2P-Regular.ttf')
		self.FONT = pg.font.Font(font_path, 14)

		self.COLOR = c.GREEN

		self.text = text
		self.txt_surface = self.FONT.render(text, True, self.COLOR)
		self.speed = 1.3 + level//20
		self.x = x
		self.y = y

	def draw(self, screen) -> None:
		# Escreve o texto na tela
		screen.blit(self.txt_surface, (self.x, self.y))

	def move(self) -> None: 
		# self.x -= self.speed
		self.y += self.speed  # Fall downward instead of moving left

	def get_width(self) -> int: 
		# retorna o comprimento da palavra
		return self.txt_surface.get_width()

#	def delete(self):
#		pass




