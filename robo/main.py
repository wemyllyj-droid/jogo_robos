import pygame
import random

pygame.init()

LARGURA = 1020
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense")
fundo = pygame.image.load("img/fundo.jpg")
fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))

explosao = pygame.image.load("img/explosão.png")

FPS = 60
clock = pygame.time.Clock()


# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image = pygame.image.load("img/player.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 5

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d]:
            self.mover(self.velocidade, 0)

        # limites de tela
        self.rect.x = max(0, min(self.rect.x, LARGURA - 20))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 95))


# TIRO (DO JOGADOR)
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image = pygame.image.load("img/tiro.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()

# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        self.image.fill((255, 0, 0))

    def atualizar_posicao(self):
        self.rect.y += self.velocidade

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()
            self.image = explosao


# ROBO EXEMPLO — ZigueZague
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image.fill((0, 0, 255))
        self.direcao = 1
        self.velocidade = 3

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3

        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
            self.direcao *= -1


class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image.fill((255, 0, 127))
        self.velocidade = 6

class RoboCiclico(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image.fill((0, 255, 0))

    
        self.base_x = x
        self.base_y = y

        self.raio = 100
        self.vel_giro = 0.4
       
        self.tabela_x = [0, 1, 2, 3, 2, 1, 0, -1, -2, -3, -2, -1]
        self.tabela_y = [-3, -2, -1, 0, 1, 2, 3, 2, 1, 0, -1, -2]

        self.indice = 0
        self.descida = 1

    def atualizar_posicao(self):
        
        self.base_y += self.descida

        self.indice = (self.indice + self.vel_giro) % len(self.tabela_x)
        i = int(self.indice)

        cx = self.tabela_x[i] * self.raio / 3
        cy = self.tabela_y[i] * self.raio / 3

        self.rect.x = self.base_x + cx
        self.rect.y = self.base_y + cy

 
        if self.rect.y > ALTURA:
            self.kill()



# grupos e objetos iniciais
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()


def reset_game():
    global jogador, todos_sprites, inimigos, tiros, pontos, spawn_timer, game_over
    # limpar grupos
    todos_sprites.empty()
    inimigos.empty()
    tiros.empty()

  
    jogador = Jogador(LARGURA // 2, ALTURA - 60)
    todos_sprites.add(jogador)

 
    pontos = 0
    spawn_timer = 0
    game_over = False



jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)


pygame.mixer.init()
pygame.mixer.music.load("sons/musica de fundo.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

tiro_som = pygame.mixer.Sound("sons/tiro.wav")
morte_som = pygame.mixer.Sound("sons/morte.wav")
item_som = pygame.mixer.Sound("sons/interação com item.wav")

pontos = 0
spawn_timer = 0

rodando = True
game_over = False
telaparada = None  

while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

     
        if game_over:
            pygame.mixer.music.set_volume(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                
                reset_game()
                pygame.mixer.init()
                pygame.mixer.music.load("sons/musica de fundo.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            continue

      
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
                todos_sprites.add(tiro)
                tiros.add(tiro)
                tiro_som.play()

    if not game_over:
        # timer de entrada dos inimigos
        spawn_timer += 1
        if spawn_timer > 80:
            x = random.randint(40, LARGURA - 40)
            y = -40
            escolha = random.randint(1, 4)
            if escolha == 1:
                robo = Robo(x, y)
            if escolha == 2:
                robo = RoboZigueZague(x, y)
            if escolha == 3:
                robo = RoboRapido(x, y)
            if escolha == 4:
                robo = RoboCiclico(x, y)
            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        # colisão tiro x robô
        colisao = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        pontos += len(colisao)

        # colisão robô x jogador
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            jogador.vida -= 1
            if jogador.vida <= 0:
                print("GAME OVER!")
                morte_som.play()
            
                telaparada = TELA.copy()
                game_over = True

    
        todos_sprites.update()

    
        TELA.blit(fundo, (0, 0))
        todos_sprites.draw(TELA)

        # Painel de pontos e vida
        font = pygame.font.SysFont(None, 30)
        texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
        TELA.blit(texto, (10, 10))

    else:
      
        if telaparada:
            TELA.blit(telaparada, (0, 0))
        else:
        
            TELA.blit(fundo, (0, 0))

        textomaior = pygame.font.SysFont(None, 64)
        textomenor = pygame.font.SysFont(None, 28)
        texto_morte = textomaior.render("VOCÊ MORREU", True, (255, 0, 0))
        instrucoes = textomenor.render("Pressione R para reiniciar", True, (255, 255, 255))

       
        rect_morte = texto_morte.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
        rect_instr = instrucoes.get_rect(center=(LARGURA // 2, ALTURA // 2 + 30))

       
        sombra = pygame.Surface((rect_morte.width + 20, rect_morte.height + 20), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 150))
        TELA.blit(sombra, (rect_morte.x - 10, rect_morte.y - 10))

        TELA.blit(texto_morte, rect_morte)
        TELA.blit(instrucoes, rect_instr)

    pygame.display.flip()

pygame.quit()
