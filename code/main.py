import pygame, sys, os, time, random
from player import Player
from alien import Alien, Extra
from random import choice, randint
from laser import Laser
import button

#----------------------------------------------------------------------------
screen_height = 600
screen_width = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Ban may bay')
#load button images
start_img = pygame.image.load('start_btn.png').convert_alpha()
nextlevel_img = pygame.image.load('harder_btn.png').convert_alpha()
exit_img = pygame.image.load('exit_btn.png').convert_alpha()
re_img = pygame.image.load('re_btn.png').convert_alpha()
title_img = pygame.image.load('title.png').convert_alpha()
#create button instances
title = button.Button(60,100,title_img,0.8)
start_button = button.Button(screen_width / 2-80, screen_height / 2+50, start_img, 0.8)
nextlevel_button = button.Button(screen_width / 2-80, screen_height / 2-100, nextlevel_img, 0.8)
exit_button = button.Button(screen_width / 2-80, screen_height / 2+150, exit_img, 0.8)
re_button = button.Button(screen_width / 2-80, screen_height / 2+50, re_img,0.8)
# Background
BG = pygame.transform.scale(pygame.image.load('../graphics/background-black.png'), (screen_width, screen_height))
hs = 0
#----------------------------------------------------------------------------
class Game:
	def __init__(self):
		# Cài đặt của Player
		player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
		self.player = pygame.sprite.GroupSingle(player_sprite)

		# HP và tính điểm
		self.lives = 3
		self.live_surf = pygame.image.load('../graphics/player.png').convert_alpha()
		self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
		self.score = 0
		#self.highest_score = 0
		self.font = pygame.font.Font('../font/Pixeled.ttf',20)
		self.time_shotting=800
		self.distance=1
		

		# Creep
		self.aliens = pygame.sprite.Group()
		self.alien_lasers = pygame.sprite.Group()
		self.alien_setup(rows = 6, cols = 8)
		self.alien_direction = 1

		# Creep 500 điểm
		self.extra = pygame.sprite.GroupSingle()
		self.extra_spawn_time = randint(40,80)

		# Nhạc nền và effect
		music = pygame.mixer.Sound('../audio/music.wav')
		music.set_volume(0.5)
		music.play(loops = -1)
		self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
		self.laser_sound.set_volume(0.2)
		self.explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
		self.explosion_sound.set_volume(0.3)

	def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
		for row_index, row in enumerate(range(rows)):
			for col_index, col in enumerate(range(cols)):
				x = col_index * x_distance + x_offset
				y = row_index * y_distance + y_offset
				
				if row_index == 0: alien_sprite = Alien('yellow',x,y)
				elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
				else: alien_sprite = Alien('red',x,y)
				self.aliens.add(alien_sprite)

	def alien_position_checker(self):
		all_aliens = self.aliens.sprites()
		for alien in all_aliens:
			if alien.rect.right >= screen_width:
				self.alien_direction = -1
				self.alien_move_down()
			elif alien.rect.left <= 0:
				self.alien_direction = 1
				self.alien_move_down()

	def alien_move_down(self):
		if self.aliens:
			for alien in self.aliens.sprites():
				alien.rect.y += self.distance

	def alien_shoot(self):
		if self.aliens.sprites():
			random_alien = choice(self.aliens.sprites())
			laser_sprite = Laser(random_alien.rect.center,6,screen_height)
			self.alien_lasers.add(laser_sprite)
			self.laser_sound.play()

	def extra_alien_timer(self):
		self.extra_spawn_time -= 1
		if self.extra_spawn_time <= 0:
			self.extra.add(Extra(choice(['right','left']),screen_width))
			self.extra_spawn_time = randint(400,800)

	def game_over(self):
		if self.lives<=0:
			music = pygame.mixer.Sound('../audio/music.wav')
			music.set_volume(0)
			music.play(loops = 0)
			self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
			self.laser_sound.set_volume(0.2)
			self.explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
			self.explosion_sound.set_volume(0.3)
			#------------------------------
			clock = pygame.time.Clock()
			clock.tick(0)
			self.extra_spawn_time = 100000
			go_surf = self.font.render('You lose',False,'white')
			go_rect = go_surf.get_rect(center = (screen_width / 2, screen_height / 2))
			#---------------------------------------------------------------------
			player_sprite = Player((-1000,-1000),-1000,5)
			self.player = pygame.sprite.GroupSingle(player_sprite)
			#---------------------------------------------------------------------
			screen.blit(go_surf,go_rect)
			if re_button.draw(screen):
				self.time_shotting=800
				self.score=0
				player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
				self.player = pygame.sprite.GroupSingle(player_sprite)
				self.aliens.empty()
				self.alien_lasers.empty()
				self.lives=3
				self.alien_setup(rows=6,cols=8)
				self.alien_shoot()
				self.extra_spawn_time=-1
				self.display_lives()
				self.player.sprite.lasers.draw(screen)
				self.player.draw(screen)
				pygame.display.update()
			elif exit_button.draw(screen):
				pygame.quit()
				sys.exit()
				pygame.display.update()

	def collision_checks(self):

		# player lasers 
		if self.player.sprite.lasers:
			for laser in self.player.sprite.lasers:				
				# alien collisions
				aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
				if aliens_hit:
					for alien in aliens_hit:
						self.score += alien.value
					laser.kill()
					self.explosion_sound.play()

				# extra collision
				if pygame.sprite.spritecollide(laser,self.extra,True):
					self.score += 500
					laser.kill()

		# alien lasers 
		if self.alien_lasers:
			for laser in self.alien_lasers:
				if pygame.sprite.spritecollide(laser,self.player,False):
					laser.kill()
					self.lives -= 1

		# aliens
		if self.aliens:
			for alien in self.aliens:
				# pygame.sprite.spritecollide(alien,self.blocks,True)
				if pygame.sprite.spritecollide(alien,self.player,False):
					self.lives-=1
					alien.kill()
	
	def display_lives(self):
		for live in range(self.lives - 1):
			x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
			screen.blit(self.live_surf,(x,8))

	def display_score(self):
		highest_score = int(getHS())
		if(highest_score < self.score):
			highest_score = self.score
		with open("hs.txt","w") as f:
			f.write(str(highest_score))
		score_surf = self.font.render(f'score: {self.score}',False,'white')
		highestscore_surf=self.font.render(f'highest: {highest_score}',False,'white')
		score_rect = score_surf.get_rect(topleft = (10,-10))
		highestscore_rect = highestscore_surf.get_rect(topleft = (10,30))
		screen.blit(score_surf,score_rect)
		screen.blit(highestscore_surf,highestscore_rect)

	def victory_message(self):
		if not self.aliens.sprites():
			if self.score >= 8000:
				#------------------
				self.extra_spawn_time = 100000
				if re_button.draw(screen):
					self.time_shotting=800
					self.score=0
					player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
					self.player = pygame.sprite.GroupSingle(player_sprite)
					self.aliens.empty()
					self.alien_lasers.empty()
					self.lives=3
					self.alien_setup(rows=6,cols=8)
					self.alien_shoot()
					self.extra_spawn_time=-1
					self.display_lives()
					self.player.sprite.lasers.draw(screen)
					self.player.draw(screen)
					pygame.display.update()
				elif exit_button.draw(screen):
					pygame.quit()
					sys.exit()
				elif nextlevel_button.draw(screen):
					self.time_shotting-=100
					self.distance+=1
					for laser in self.player.sprite.lasers:				
						laser.kill()
					self.alien_lasers.empty()
					self.alien_setup(rows=6,cols=8)
					ALIENLASER = pygame.USEREVENT + 1
					pygame.time.set_timer(ALIENLASER,self.time_shotting)
					self.alien_shoot()
					self.player.sprite.lasers.draw(screen)
					self.player.draw(screen)
					pygame.display.update()

				#------------------
				victory_surf = self.font.render('You won',False,'white')
				victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
				screen.blit(victory_surf,victory_rect)


	def run(self):
		self.player.update()
		self.alien_lasers.update()
		self.extra.update()
		
		self.aliens.update(self.alien_direction)
		self.alien_position_checker()
		self.extra_alien_timer()
		self.collision_checks()

		self.player.sprite.lasers.draw(screen)
		self.player.draw(screen)
		# self.blocks.draw(screen)
		self.aliens.draw(screen)
		self.alien_lasers.draw(screen)
		self.extra.draw(screen)
		self.display_lives()
		self.display_score()
		self.victory_message()
		self.game_over()

def getHS():
	with open("HS.txt","r") as f:
		return f.read()

def maingame():
	screen_width = 600
	screen_height = 600
	screen = pygame.display.set_mode(( screen_width,screen_height))
	pygame.init()
	clock = pygame.time.Clock()
	game = Game()


	ALIENLASER = pygame.USEREVENT + 1
	pygame.time.set_timer(ALIENLASER,game.time_shotting)
	try:
		highest_score = int(getHS())
	except:
		highest_score = 0
	#game loop
	while True:
		screen.fill((202, 228, 241))
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == ALIENLASER:
				game.alien_shoot()
		#crt.draw()
		screen.blit(BG, (0,0))
		#screen.fill((30,30,30))
		game.run()
		pygame.display.flip()
		clock.tick(60)

#game loop
run = True
while run:
	WIN = pygame.display.set_mode((screen_width, screen_height))
	WIN.blit(BG, (0,0))
	title.draw(screen)
	if start_button.draw(screen):
		print('START')
		maingame()
	if exit_button.draw(screen):
		print('EXIT')
		pygame.quit()
		sys.exit()

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()