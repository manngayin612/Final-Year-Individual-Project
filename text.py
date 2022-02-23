import pygame
from pygame import display



#define RGB
white = [255, 255, 255]
black = [0, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]

X = 400
Y = 400

# create rectangle
input_rect = pygame.Rect(200, 200, 140, 32)
color_active = pygame.Color('lightskyblue3')
  
# color_passive store color(chartreuse4) which is
# color of input box.
color_passive = pygame.Color('chartreuse4')
color = color_passive
  
active = False

pygame.init()



font = pygame.font.Font("Kaiso-Next-B.otf", 32)
display_surface = pygame.display.set_mode((X,Y))
pygame.display.set_caption("Show Text")


lines = ["Welcome to the game", 
        "What is your name?",
        "Are you ready?",
        "Let's Go!"]


count = 0
user_input = ""

def renderLine(line):
    print("rendering", line)
    text = font.render(line, True, white, black)
    textRect = text.get_rect()
    textRect.center = (X//2, Y//2)
    display_surface.fill(black)
    display_surface.blit(text, textRect)



def handle_keys():
    global count, active, user_input

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
    
            if event.key == pygame.K_SPACE:
                print("pressed SPACE BAR")
                count += 1
                renderLine(lines[count])
            elif event.key == pygame.K_RETURN:
                user_input = user_input[:-1]
                user_input = ""
                active = False
                print("Submitting")
                count += 1
                renderLine(lines[count])
                
            else:
                user_input += event.unicode
                print(user_input)
                

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if input_rect.collidepoint(event.pos):
                print("waiting for input")
                active = True
            else:
                active = False

    if active:
        color = color_active
    else:
        color = color_passive




renderLine(lines[count])

while True:

    handle_keys()
    pygame.draw.rect(display_surface, color, input_rect)

    text_surface = font.render(user_input, True, (255, 255, 255))
        
    # render at position stated in arguments
    display_surface.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        
    # set width of textfield so that text cannot get
    # outside of user's text input
    input_rect.w = max(100, text_surface.get_width()+10)
        
    # display.flip() will update only a portion of the
    # screen to updated, not full area
    pygame.display.flip()
        
    pygame.display.update()

