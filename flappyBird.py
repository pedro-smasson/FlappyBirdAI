import pygame
import random
import os
import neat

pygame.font.init()

# DEFININDO A ESTRUTURA BÁSICA DO AMBIENTE/TELA
altura = 700
largura = 600
chao = 700
fonte = pygame.font.SysFont("arial", 50)
inicializarTelaJogo = False
telaJogo = pygame.display.set_mode((largura, altura))

pygame.display.set_caption("Flappy Bird UI")

# DEFININDO AS IMAGENS QUE SERÃO UTILIZADAS COMO "SPRITE" DO FLAPPY/PARTES DO CENÁRIO
imgFlappy = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
imgObstaculo = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
imgTerreno = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())
imgbackground = pygame.transform.scale(pygame.image.load(os.path.join("imgs","background.png")).convert_alpha(), (600, 900))

# DEFININDO O COMPORTAMENTO E AÇÕES DO FLAPPY
class FlappyBird:

    frameFlappy = imgFlappy
    rotacaoMaximaFlappy = 20
    velocidadeRotacao = 20
    delayAnimacao = 5

    def __init__(flappy, x, y):

        flappy.x = x
        flappy.y = y
        flappy.queda = 0
        flappy.alturaPulo = 0
        flappy.totalFrames = 0
        flappy.altura = flappy.y
        flappy.contadorQuedas = 0
        flappy.frameAtual = flappy.frameFlappy[0]

    def pular(flappy):

        flappy.alturaPulo = -11
        flappy.altura = flappy.y
        flappy.contadorQuedas = 0

    def mover(flappy):

        flappy.contadorQuedas += 1
        deslocamentoTotal = flappy.alturaPulo * (flappy.contadorQuedas) + 0.5 * 3 * (flappy.contadorQuedas) ** 2

        if deslocamentoTotal >= 16:
            deslocamentoTotal = (deslocamentoTotal / abs(deslocamentoTotal)) * 16

        if deslocamentoTotal < 0:
            deslocamentoTotal -= 2

        flappy.y = flappy.y + deslocamentoTotal

        if deslocamentoTotal < 0 or flappy.y < flappy.altura + 50:
            if flappy.queda < flappy.rotacaoMaximaFlappy:
                flappy.queda = flappy.rotacaoMaximaFlappy
        else:
            if flappy.queda > -90:
                flappy.queda -= flappy.velocidadeRotacao

    def criarTela(flappy, telaJogo):

        flappy.totalFrames += 1

        if flappy.totalFrames <= flappy.delayAnimacao:
            flappy.frameAtual = flappy.frameFlappy[0]
        elif flappy.totalFrames <= flappy.delayAnimacao*2:
            flappy.frameAtual = flappy.frameFlappy[1]
        elif flappy.totalFrames <= flappy.delayAnimacao*3:
            flappy.frameAtual = flappy.frameFlappy[2]
        elif flappy.totalFrames <= flappy.delayAnimacao*4:
            flappy.frameAtual = flappy.frameFlappy[1]
        elif flappy.totalFrames == flappy.delayAnimacao*4 + 1:
            flappy.frameAtual = flappy.frameFlappy[0]
            flappy.totalFrames = 0

        if flappy.queda <= -80:
            flappy.frameAtual = flappy.frameFlappy[1]
            flappy.totalFrames = flappy.delayAnimacao*2

        blitRotateCenter(telaJogo, flappy.frameAtual, (flappy.x, flappy.y), flappy.queda)

    def maskflappy(flappy):
        return pygame.mask.from_surface(flappy.frameAtual)

# DEFININDO OS ATRIBUTOS E COMPORTAMENTO DO OBSTÁCULO
class Obstaculo():

    velocidadeAtual = 5
    distanciaEntreObstaculos = 200

    def __init__(flappy, x):

        flappy.x = x
        flappy.top = 0
        flappy.altura = 0
        flappy.bottom = 0
        flappy.passouObstaculo = False
        flappy.obstaculoBaixo = imgObstaculo
        flappy.obstaculoCima = pygame.transform.flip(imgObstaculo, False, True)
        
        flappy.set_altura()

    def set_altura(flappy):
        
        flappy.altura = random.randrange(50, 450)
        flappy.top = flappy.altura - flappy.obstaculoCima.get_height()
        flappy.bottom = flappy.altura + flappy.distanciaEntreObstaculos

    def mover(flappy):
        flappy.x -= flappy.velocidadeAtual

    def criarTela(flappy, telaJogo):

        telaJogo.blit(flappy.obstaculoCima, (flappy.x, flappy.top))
        telaJogo.blit(flappy.obstaculoBaixo, (flappy.x, flappy.bottom))

    def colisaoComObstaculo(flappy, bird, telaJogo):

        maskAtualflappy = bird.maskflappy()
        colidiuEmCima = pygame.mask.from_surface(flappy.obstaculoCima)
        colidiuEmBaixo = pygame.mask.from_surface(flappy.obstaculoBaixo)
        deslocamentoCima = (flappy.x - bird.x, flappy.top - round(bird.y))
        deslocamentoBaixo = (flappy.x - bird.x, flappy.bottom - round(bird.y))
        pontoDeColisaoEmBaixo = maskAtualflappy.overlap(colidiuEmBaixo, deslocamentoBaixo)
        pontoDeColisaoEmCima = maskAtualflappy.overlap(colidiuEmCima,deslocamentoCima)

        if pontoDeColisaoEmBaixo or pontoDeColisaoEmCima:
            return True
        return False

# DEFININDO OS ATRIBUTOS E COMPORTAMENTO DO TERRRENO
class Terreno:

    velocidadeAtual = 5
    largura = imgTerreno.get_width()
    imgTerreno = imgTerreno

    def __init__(flappy, y):

        flappy.y = y
        flappy.x1 = 0
        flappy.x2 = flappy.largura

    def mover(flappy):

        flappy.x1 -= flappy.velocidadeAtual
        flappy.x2 -= flappy.velocidadeAtual

        if flappy.x1 + flappy.largura < 0:
            flappy.x1 = flappy.x2 + flappy.largura

        if flappy.x2 + flappy.largura < 0:
            flappy.x2 = flappy.x1 + flappy.largura

    def criarTela(flappy, telaJogo):

        telaJogo.blit(flappy.imgTerreno, (flappy.x1, flappy.y))
        telaJogo.blit(flappy.imgTerreno, (flappy.x2, flappy.y))


def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def telaFinalDoJogo(telaJogo, passarosRestantes, obstaculos, terreno, pontuacaoAtual, pipe_ind):

    telaJogo.blit(imgbackground, (0,0))

    for pipe in obstaculos:
        pipe.criarTela(telaJogo)

    terreno.criarTela(telaJogo)
    for passaro in passarosRestantes:
        if inicializarTelaJogo:
            try:
                pygame.criarTela.line(telaJogo, (255,0,0), (passaro.x+passaro.frameAtual.get_width()/2, passaro.y + passaro.frameAtual.get_height()/2), (obstaculos[pipe_ind].x + obstaculos[pipe_ind].obstaculoCima.get_width()/2, obstaculos[pipe_ind].altura), 5)
                pygame.criarTela.line(telaJogo, (255,0,0), (passaro.x+passaro.frameAtual.get_width()/2, passaro.y + passaro.frameAtual.get_height()/2), (obstaculos[pipe_ind].x + obstaculos[pipe_ind].obstaculoBaixo.get_width()/2, obstaculos[pipe_ind].bottom), 5)
            except:
                pass
        passaro.criarTela(telaJogo)

    lblPontuacao = fonte.render("Pontos: " + str(pontuacaoAtual),1,(255,255,255))
    telaJogo.blit(lblPontuacao, (largura - lblPontuacao.get_width() - 15, 10))

    lblPontuacao = fonte.render("Vivos: " + str(len(passarosRestantes)),1,(255,255,255))
    telaJogo.blit(lblPontuacao, (10, 10))

    pygame.display.update()

# A PARTIR DAQUI COMEÇA A MANIPULAÇÃO DE INTELIGÊNCIA ARTIFICIAL #
def genomas(individuos, config):

    global telaJogo
    telaJogo = telaJogo

    nets = []
    passaroAI = []
    genoma = []

    for id_Individuo, individuo in individuos:
        individuo.fitness = 0
        gerarAI = neat.nn.FeedForwardNetwork.create(individuo, config)
        nets.append(gerarAI)
        passaroAI.append(FlappyBird(230,350))
        genoma.append(individuo)

    terrenoFinal = Terreno(chao)
    obstaculos = [Obstaculo(700)]
    pontuacaoAtual = 0

    tempo = pygame.time.Clock()

    run = True
    while run and len(passaroAI) > 0:
        tempo.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(passaroAI) > 0:
            if len(obstaculos) > 1 and passaroAI[0].x > obstaculos[0].x + obstaculos[0].obstaculoCima.get_width():  
                pipe_ind = 1                                                                

        for x, bird in enumerate(passaroAI):
            genoma[x].fitness += 0.1
            bird.mover()

            output = nets[passaroAI.index(bird)].activate((bird.y, abs(bird.y - obstaculos[pipe_ind].altura), abs(bird.y - obstaculos[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.pular()

        terrenoFinal.mover()

        rem = []
        add_pipe = False
        for pipe in obstaculos:
            pipe.mover()
            for bird in passaroAI:
                if pipe.colisaoComObstaculo(bird, telaJogo):
                    genoma[passaroAI.index(bird)].fitness -= 1
                    nets.pop(passaroAI.index(bird))
                    genoma.pop(passaroAI.index(bird))
                    passaroAI.pop(passaroAI.index(bird))

            if pipe.x + pipe.obstaculoCima.get_width() < 0:
                rem.append(pipe)

            if not pipe.passouObstaculo and pipe.x < bird.x:
                pipe.passouObstaculo = True
                add_pipe = True

        if add_pipe:
            pontuacaoAtual += 1
            for individuo in genoma:
                individuo.fitness += 5
            obstaculos.append(Obstaculo(largura))

        for r in rem:
            obstaculos.remove(r)

        for bird in passaroAI:
            if bird.y + bird.frameAtual.get_height() - 10 >= chao or bird.y < -50:
                nets.pop(passaroAI.index(bird))
                genoma.pop(passaroAI.index(bird))
                passaroAI.pop(passaroAI.index(bird))

        telaFinalDoJogo(telaJogo, passaroAI, obstaculos, terrenoFinal, pontuacaoAtual, pipe_ind)


def run(populando):
    
    configurandoAI = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, populando)
    AIs = neat.Population(configurandoAI)

    AIs.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    AIs.add_reporter(stats)

    AIs.run(genomas, 30)

if __name__ == '__main__':
    diretorioLocal = os.path.dirname(__file__)
    configAI = os.path.join(diretorioLocal, 'configAI.txt')
    run(configAI)