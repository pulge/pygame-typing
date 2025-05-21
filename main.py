from game import Game
import sys

def main(word_list: str):
	game = Game(word_list)
	while game.running:
		game.start()

if __name__ == '__main__':
	word_list = 'python'
	if len(sys.argv) > 1:
		word_list = str(sys.argv[1])
	main(word_list)
