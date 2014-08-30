import pygame
import signal

def close_all(signal, frame):
    pygame.quit()   
#in case of SIGINT (kill, etc) perform a nice shut down    
signal.signal(signal.SIGINT, close_all)




def draw_ui(screen):
        pygame.draw.polygon(screen,(0,0,0),((0,475),(635,475),(635,0),(800,0),
                (800,600),(0,600)))
        font = pygame.font.Font(None, 36)
        
        pygame.draw.rect(screen,(255,0,0),(645,5,150,100), 2)
        text = font.render("JOYAXISMOTION:", 1, (255, 255, 255))
        screen.blit(text,(650,10))



#start SDL stuff

pygame.init()
pygame.joystick.init()
pygame.joystick.Joystick(0).init()

pygame.display.set_caption('Joystic Test')
screen = pygame.display.set_mode((800,600))
draw_ui(screen) 
pygame.display.flip()

Finish =False

while not Finish:
	event=pygame.event.poll()

	if event.type==pygame.JOYAXISMOTION:
		print ('JOYAXISMOTION' 'Axis:', event.axis,  'Value:', event.value)