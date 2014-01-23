import pygame, random, sys, os
from pygame.locals import *

def collide(x1, x2, y1, y2, w1, w2, h1, h2):
	return x2 < x1 + w1 and x1 < x2 + w2 and  y2 < y1 + h1 and y1 < y2 + h2


class Tetris:
	block_size = 20
	win_w = 280
	win_h = 600

	#shape is the current shape
	shape = []
	level = 1
	score = 0
		
	target_pos = 100,100

	#declare and fill tetris grid
	tetris_grid=[]
	texture_grid =[]
	#fill tetris grid initially
	


	w = None
	font = None
	clock = None
	block_surface = None 
	shape_surface = None
	is_moving = None
	
	cumulative_x = []
	cumulative_y = []
	
	#initialize textures
	current_shape_no = 0
	textures = ["block0.png","block1.png","block2.png","block3.png","block4.png","block5.png","block6.png"]
	surfaces = []
	theme_snd = None
	effect_snd = []
	
	def __init__(self):
		for i in self.textures:
			self.surfaces.append(pygame.image.load(i))
		
		initial_line = []
		for i in range(0,self.win_w/self.block_size):
			obj=i*self.block_size,0
			initial_line.append(obj)
		self.tetris_grid.append(initial_line)
	
		self.pick_next_shape()
		pygame.init()
		self.w=pygame.display.set_mode((self.win_w, self.win_h))
		pygame.display.set_caption('GAME320 Tetris')
		
		

		self.font = pygame.font.Font(None, 20)
		self.clock = pygame.time.Clock()

		#########################################
		#block
		self.block_surface = pygame.Surface((self.block_size,self.block_size))
		self.block_surface.fill((0, 255, 0))

		#initialize sound
		pygame.mixer.init()	
		self.theme_snd = pygame.mixer.Sound("theme.ogg")
		self.effect_snd.append(pygame.mixer.Sound("effect1.ogg"))
		self.effect_snd.append(pygame.mixer.Sound("effect2.ogg"))
		self.effect_snd.append(pygame.mixer.Sound("effect3.ogg"))
		#initialize theme sound
		self.theme_snd.set_volume(0.4) #make it "twice" software
		self.theme_snd.play(-1)
		
		#shape
		#self.shape_surface = pygame.Surface((self.block_size,self.block_size))
		#self.shape_surface.fill((255, 0, 0))
		#update_shape((win_w - block_size)/4,0) #initial position of shape
		self.update_shape(self.win_w/2,0) #initial position of shape
		self.update()
	
	########################################
	def update_shape(self,x,y):		
		count = 0
		for i in self.shape:
			i[0]+=x
			i[1]+=y
			
			if len(self.cumulative_x)-1 < count:
				self.cumulative_x.append(x)
				self.cumulative_y.append(y)
			else:
				self.cumulative_x[count]+=x #need this for rotation
				self.cumulative_y[count]+=y
			
			count+=1
	def display_shape(self):
		for i in self.shape:
			self.w.blit(self.shape_surface,(i[0],i[1]))

	'''def game_over(self):
		game_over_str = 'Game Over' 
		t=font.render(game_over_str, True, (255, 255, 255))
		w.blit(t, ((win_w - falling_shape_w) - 80, 0))
		pygame.display.update()
		pygame.time.wait(2000)
		sys.exit(0)'''

	def rotate_shape(self):
		#sin90 = 1
		#cos90 = 0
		#x' = cos(theta)*x - sin(theta)*y 
		#y' = sin(theta)*x + cos(theta)*y
		#So,
		#x' = -y
		#y' = x
		
		#play a sound when rotating
		self.effect_snd[0].play()
		count = 0
		for i in self.shape:
			#translate to origin
			i[0] -= self.cumulative_x[count]
			i[1] -= self.cumulative_y[count]
			print i[0],i[1]
			
			#rotate
			x = i[0]
			y = i[1]
			i[0] = -y
			i[1] = x
			
			#translate back
			i[0] += self.cumulative_x[count]
			i[1] += self.cumulative_y[count]
			count+=1
		self.check_if_off()
		
	def move_shape_down(self,amount):
		#first thing you do is you shift
		self.update_shape(0,amount)
	
	
	def check_if_off(self):
		#check to see if the shift is legal:
		#we go through all the blocks in the shape
		its_off_by = 0
		for i in self.shape:
			if i[0] < 0:
				its_off_by = -i[0]
			elif i[0] > self.win_w-self.block_size:
				its_off_by = (i[0]-self.win_w-self.block_size)
		
		#now if its off by some amount, return it to proper position
		if its_off_by !=0:
			self.update_shape(its_off_by,0)	
	
	def shift_shape(self,amount):
		#first thing you do is you shift
		self.update_shape(amount,0)
		self.check_if_off()
		
	def move(self):
		if self.is_moving == 'Left':
			 self.shift_shape(-self.block_size)
		elif self.is_moving == 'Right':
			self.shift_shape(self.block_size)
		elif self.is_moving == 'Down':
			self.move_shape_down(self.block_size)


	def input(self,events): 
		for e in events:
			if e.type == QUIT:
				sys.exit(0)
			elif e.type == KEYDOWN:
				if e.key == K_UP:
					self.rotate_shape()#self.is_moving = 'Up'
				elif e.key == K_DOWN:
					self.is_moving = 'Down'
				elif e.key == K_LEFT:
					self.is_moving = 'Left'
				elif e.key == K_RIGHT:
					self.is_moving = 'Right'
			elif e.type == KEYUP:
				self.is_moving = None

	
	def pick_next_shape(self): #randomly
		print "picking"
		#self.speed = self.level*self.speed #reset speed
		del self.shape[:]
		path = os.getcwd()+'/'+'shapes.txt'
		f = open (path,'r')
		lines = f.readlines()
		random_shape = random.randint(0,len(lines)-1)
		self.shape_surface = self.surfaces[random_shape]
		self.current_shape_no = random_shape
		count = 0
		last_duo = None
		line = lines[random_shape].split(',')
		for i in line:
			if count % 2 == 0:
				duo = []
				duo.append(int(i)*self.block_size)
				self.shape.append(duo)
				last_duo = duo				
			else:
				last_duo.append(int(i)*self.block_size)
			count+=1
		
		del self.cumulative_x[:]
		del self.cumulative_y[:]
	
	def check_clear_lines(self):
		#to_pop = []
		for i in range (1,len(self.tetris_grid)):
			#self.tetris_grid[i].sort()
			#print self.tetris_grid[i],len(self.tetris_grid[i])
			
			remove = True
			
			filtered_line = []
			for k in self.tetris_grid[i]:
				filtered_line.append(k[0])
				
			
			for j in range (0,self.win_w,self.block_size):
				remove = remove and j in filtered_line
			if remove:
				self.score+=1
				if self.score % 5 == 0 and self.score > 0:	#after every 5 cleares increase level
					self.level+=1
					
				self.tetris_grid.pop(i)
				self.check_clear_lines()
				self.effect_snd[2].play() #play clear sound
				break

		#if found any them pop them
	
	def drop(self):
		grid_no = 0
		for line in self.tetris_grid:
			for j in line:
				for i in self.shape: 
					if collide(i[0], j[0], i[1], self.win_h-grid_no*self.block_size, self.block_size, self.block_size, self.block_size, self.block_size):
						
						#lets first, if it left or right sides, collided, if so, then ignore them
						#by putting the shape back where it was
						if self.is_moving == 'Left':
							self.update_shape(self.block_size,0)
							return
						elif self.is_moving == 'Right':
							self.update_shape(-self.block_size,0)
							return
						#when first collision happen, disable controls, then re-enable them when next
						#shape is picked
						self.effect_snd[1].play() #play collide sound
						print "collide",i[1],self.win_h-grid_no*self.block_size
						#self.speed = 2
						for k in self.shape: 
							v_dist = (i[1]-k[1])/self.block_size #displacement for line
							while len(self.tetris_grid) <= grid_no+1+v_dist: #add a line if one doesn't exist
								self.tetris_grid.append([])						
							self.tetris_grid[grid_no+1+v_dist].append((k[0],self.current_shape_no)) #and maybe delete
						self.check_clear_lines()
						self.pick_next_shape()
						self.update_shape(self.win_w/2,0) #put it into the middle of the screen
						return
			grid_no+=1
	
	def update(self):
		frame = 0
		while True:
			self.clock.tick(30)
			frame+=1
			
			self.input(pygame.event.get()) 				#1
			self.move() #if there is something to move  #2
			
			if frame % int(30/self.level) == 0 and self.is_moving == None:
				self.update_shape(0,self.block_size)	  			#3


			self.drop()
			self.w.fill((0, 0, 0))		  		
			#before blitting the target make sure its not outside the window

			t=self.font.render('Level:'+str(self.level)+' Score:'+str(self.score), True, (255, 255, 255))
			self.w.blit(t, (10, 10))

			#display grid
			y = 0
			for i in self.tetris_grid:
				for j in i:	
					self.w.blit(self.surfaces[j[1]],(j[0],self.win_h-y*self.block_size))	#its 600 without block_size
				y+=1
			#display shape
			self.display_shape()
			pygame.display.update()

Tetris()