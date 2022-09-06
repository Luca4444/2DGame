import math
import pygame
import sys

pygame.init()
pygame.display.set_caption('Luca Game')
size = widthS, heightS = 1000, 800
black = 0, 0, 0

screen = pygame.display.set_mode(size)
red = (255, 0, 0)
green = (124, 252, 0)

playerProgress = {
    "playerOutfit": 0,
    "playerUnlockedOutfits": [1, 0, 0, 0, 0],
    "playerGun": 1,
    "playerLife": 4,
    "playerCoins": 100,
}

levelProgress = {
    "mainHouse": 0,
    "mainPatio": ["haunted", "haunted", "haunted"],
    "firstHouse": 0,
    "secondHouse": 0,
    "thirdHouse": 0
}


def scoreText(score, x, y, txt, fontSize, fontColor):
    font = pygame.font.Font('Minecraft.ttf', fontSize)
    if score == False:
        text = font.render(txt, True, fontColor)
    else:
        text = font.render(txt + str(score), True, fontColor)

    textRect = text.get_rect()
    textRect.center = (x, y)
    return [text, textRect]


def door(doorsInfo):  # [doorRect, playerRect, targetLevel, type(1=check collision, 2=direct), levelInfo]
    if len(doorsInfo) > 0:
        if doorsInfo[3] == 1:
            if doorsInfo[1].colliderect(doorsInfo[0]):
                game = Game(doorsInfo[2])
                game.main()
                return True
            else:
                return False
        elif doorsInfo[3] == 2:
            game = Game(doorsInfo[2])
            game.main()
            return True


class Game:
    def __init__(self, level):
        self.level = level()
        self.levelVar = level
        self.screen = screen
        self.player = self.level.player
        self.score = 1

    def main(self):
        clock = pygame.time.Clock()
        frametime = clock.tick()
        self.score = 1
        run = True
        while run == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    sys.exit()

            if door(self.level.doorsInfo):
                run = False

            self.drawObjects()

            clock.tick(50)

    def drawObjects(self):
        self.level.drawBackGround(screen, widthS, heightS)
        if playerProgress["playerLife"] <= 0:

            def interactableRetry():
                playerProgress["playerOutfit"] = self.level.previousPlayerProgress["playerOutfit"]
                playerProgress["playerGun"] = self.level.previousPlayerProgress["playerGun"]
                playerProgress["playerLife"] = self.level.previousPlayerProgress["playerLife"]
                playerProgress["playerCoins"] = self.level.previousPlayerProgress["playerCoins"]
                self.level.interactable = None
                door([0, 0, self.levelVar, 2, None])

            def interactableExit():
                playerProgress["playerOutfit"] = self.level.previousPlayerProgress["playerOutfit"]
                playerProgress["playerGun"] = self.level.previousPlayerProgress["playerGun"]
                playerProgress["playerLife"] = self.level.previousPlayerProgress["playerLife"]
                playerProgress["playerCoins"] = self.level.previousPlayerProgress["playerCoins"]
                self.level.interactable = None
                door([0, 0, Level1, 2, None])

            self.level.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 200,
                                                   "Level Failed :(",
                                                   [["Retry", interactableRetry], ["Exit House", interactableExit]])
        else:
            self.player.move()
        self.level.drawDecor(self.screen)
        self.level.drawHousesBehind(self.screen, self.player.playerRect.y)
        self.level.drawWallsBehind(self.screen, self.player.playerRect.y)

        if len(self.level.enemysList) != 0:
            self.level.drawMoveEnemy(self.screen)
        else:
            if self.level.enemyWave is not None:
                if self.level.enemyWave == -1:
                    self.level.endLevel()
                elif self.level.enemyWave >= 0:
                    self.level.enemyWave -= 1
                    if self.level.enemyWave != -1:
                        self.level.enemyWaveList[self.level.enemyWave]()

        self.player.drawPlayer(self.screen)

        self.level.drawHousesFront(self.screen, self.player.playerRect.y)
        self.level.drawWallsFront(self.screen, self.player.playerRect.y)

        self.level.drawInteractableObjects(screen)

        self.player.drawLifes(screen)
        self.player.drawCoins(screen)

        if self.level.interactable is not None:
            self.level.interactable.drawInteractable(self.screen)

        pygame.display.update()


class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, xPOS, yPOS, walls, speed=4):
        super().__init__()
        self.heartImage = pygame.transform.scale(pygame.image.load("pictures/heartGame.png").convert_alpha(), (32, 28))
        self.blackSpot = pygame.transform.scale(pygame.image.load("pictures/spotBlack2.png").convert_alpha(),
                                                (2800, 2240))
        self.coinImage = pygame.transform.scale(pygame.image.load("pictures/coinGame.png").convert_alpha(), (32, 32))
        self.blackSpot.set_alpha(250)
        self.blackSpotRect = self.blackSpot.get_rect()
        self.bulletList = []
        self.attackMode = False
        self.speed = speed

        self.shootSpeed = 0
        self.spriteSheetImages = [
            ["pictures/PlayerSpritesheet.png", "pictures/PlayerShootingGun.png"],
            ["pictures/PlayerSpriteSheetGreen.png", "pictures/PlayerShootingGun.png"],
            ["pictures/PlayerSpriteSheetPink.png", "pictures/PlayerShootingGun.png"],
            ["pictures/PlayerSpriteSheetRed.png", "pictures/PlayerShootingGun.png"],
            ["pictures/PlayerSpriteSheetYellow.png", "pictures/PlayerShootingGun.png"],
        ]

        self.playerRect = pygame.rect.Rect((xPOS, yPOS, width, height))
        self.wallToCheck = []
        print(walls)
        for wall in walls:
            self.wallToCheck.append(wall.getRect())
        self.spriteSheet = pygame.image.load(self.spriteSheetImages[playerProgress["playerOutfit"]][0]).convert_alpha()
        # self.spriteSheet.set_alpha(10)
        #   16 66 116 166 216
        # 5
        # 50
        # 105
        # 155
        # 205
        self.playerIdleCoor = [[[16, 5], [18, 39]]]

        self.playerWalkingUpCoor = [
            [[66, 5], [18, 39]],
            [[116, 5], [18, 39]],
            [[166, 5], [18, 39]],
            [[116, 5], [18, 39]],
            [[66, 5], [18, 39]],
            [[216, 5], [18, 39]],
            [[16, 55], [18, 39]],
            [[216, 5], [18, 39]]]

        self.playerWalkingDownCoor = [
            [[66, 55], [18, 39]],
            [[116, 55], [18, 39]],
            [[166, 55], [18, 39]],
            [[116, 55], [18, 39]],
            [[66, 55], [18, 39]],
            [[216, 55], [18, 39]],
            [[16, 105], [18, 39]],
            [[216, 55], [18, 39]]]

        self.playerWalkingRigthCoor = [
            [[66, 105], [18, 39]],
            [[116, 105], [18, 39]],
            [[166, 105], [18, 39]],
            [[116, 105], [18, 39]],
            [[66, 105], [18, 39]],
            [[216, 105], [18, 39]],
            [[16, 155], [18, 39]],
            [[216, 105], [18, 39]]]

        self.playerWalkingLeftCoor = [
            [[66, 155], [18, 39]],
            [[116, 155], [18, 39]],
            [[166, 155], [18, 39]],
            [[116, 155], [18, 39]],
            [[66, 155], [18, 39]],
            [[216, 155], [18, 39]],
            [[16, 205], [18, 39]],
            [[216, 155], [18, 39]]]

        self.playerWalkingRigthCoorShooting = [
            [[69, 105], [24, 39]],
            [[119, 105], [24, 39]],
            [[169, 105], [24, 39]],
            [[119, 105], [24, 39]],
            [[69, 105], [24, 39]],
            [[219, 105], [24, 39]],
            [[19, 155], [24, 39]],
            [[219, 105], [24, 39]]]

        self.playerWalkingLeftCoorShooting = [
            [[57, 155], [24, 39]],
            [[107, 155], [24, 39]],
            [[157, 155], [24, 39]],
            [[107, 155], [24, 39]],
            [[57, 155], [24, 39]],
            [[207, 155], [24, 39]],
            [[7, 205], [24, 39]],
            [[207, 155], [24, 39]]]

        self.idle = True
        self.counterImages = 0
        self.imageRate = 0.3
        self.imageCurrentList = self.playerIdleCoor

        self.wallsCollided = []

    def move(self):

        keys = pygame.key.get_pressed()
        self.checkWalls(self.wallToCheck)

        if self.attackMode == True:
            # draw life
            mouse = pygame.mouse.get_pos()
            if self.shootSpeed > 0:
                self.shootSpeed -= 1
            mouseButtons = pygame.mouse.get_pressed()
            if mouseButtons == (1, 0, 0) and self.shootSpeed == 0:
                bullet = Bullet(4, 4, self.playerRect, speed=12)
                bullet.setUpBullet()
                self.bulletList.append(bullet)
                self.shootSpeed += 10

            mouseX = self.playerRect.x - mouse[0]
            # mouseY = self.playerRect.y - mouse[1]
            for bullet in self.bulletList:
                bullet.move()

            if mouseX < 0:
                if (mouseX * -1) + self.playerRect.y > mouse[1]:
                    if self.playerRect.y - (mouseX * -1) > mouse[1]:
                        if self.idle == True:
                            self.imageCurrentList = [self.playerWalkingUpCoor[0]]
                            self.counterImages = 0
                        else:
                            self.counterImages += self.imageRate
                            self.imageCurrentList = self.playerWalkingUpCoor
                            if self.counterImages > len(self.imageCurrentList) - 2:
                                self.counterImages = 0
                    else:
                        if self.idle == True:
                            self.imageCurrentList = [self.playerWalkingRigthCoorShooting[0]]
                            self.counterImages = 0
                        else:
                            self.counterImages += self.imageRate
                            self.imageCurrentList = self.playerWalkingRigthCoorShooting
                            if self.counterImages > len(self.imageCurrentList) - 2:
                                self.counterImages = 0
                else:
                    if self.idle == True:
                        self.imageCurrentList = [self.playerWalkingDownCoor[0]]
                        self.counterImages = 0
                    else:
                        self.counterImages += self.imageRate
                        self.imageCurrentList = self.playerWalkingDownCoor
                        if self.counterImages > len(self.imageCurrentList) - 2:
                            self.counterImages = 0
            elif mouseX >= 0:
                if mouseX + self.playerRect.y > mouse[1]:
                    if self.playerRect.y - mouseX > mouse[1]:
                        if self.idle == True:
                            self.imageCurrentList = [self.playerWalkingUpCoor[0]]
                            self.counterImages = 0
                        else:
                            self.counterImages += self.imageRate
                            self.imageCurrentList = self.playerWalkingUpCoor
                            if self.counterImages > len(self.imageCurrentList) - 2:
                                self.counterImages = 0
                    else:
                        if self.idle == True:
                            self.imageCurrentList = [self.playerWalkingLeftCoorShooting[0]]
                            self.counterImages = 0
                        else:
                            self.counterImages += self.imageRate
                            self.imageCurrentList = self.playerWalkingLeftCoorShooting
                            if self.counterImages > len(self.imageCurrentList) - 2:
                                self.counterImages = 0
                else:
                    if self.idle == True:
                        self.imageCurrentList = [self.playerWalkingDownCoor[0]]
                        self.counterImages = 0
                    else:
                        self.counterImages += self.imageRate
                        self.imageCurrentList = self.playerWalkingDownCoor
                        if self.counterImages > len(self.imageCurrentList) - 2:
                            self.counterImages = 0

        if keys[pygame.K_a] and not keys[pygame.K_d] and "right" not in self.wallsCollided:
            if not keys[pygame.K_w] and not keys[pygame.K_s]:
                self.playerRect.move_ip(-self.speed, 0)
                self.idle = False

            if keys[pygame.K_w] and not keys[pygame.K_s] and "down" not in self.wallsCollided:
                self.playerRect.move_ip(-self.speed / math.sqrt(2), -self.speed / math.sqrt(2))
                self.idle = False

            if keys[pygame.K_s] and not keys[pygame.K_w] and "up" not in self.wallsCollided:
                self.playerRect.move_ip(-self.speed / math.sqrt(2), self.speed / math.sqrt(2))
                self.idle = False

            if self.attackMode == False:
                self.counterImages += self.imageRate
                self.imageCurrentList = self.playerWalkingLeftCoor
                if self.counterImages > len(self.imageCurrentList) - 2:
                    self.counterImages = 0

        if keys[pygame.K_d] and not keys[pygame.K_a] and "left" not in self.wallsCollided:
            if not keys[pygame.K_w] and not keys[pygame.K_s]:
                self.playerRect.move_ip(self.speed, 0)
                self.idle = False

            if keys[pygame.K_w] and not keys[pygame.K_s] and "down" not in self.wallsCollided:
                self.playerRect.move_ip(self.speed / math.sqrt(2), -self.speed / math.sqrt(2))
                self.idle = False

            if keys[pygame.K_s] and not keys[pygame.K_w] and "up" not in self.wallsCollided:
                self.playerRect.move_ip(self.speed / math.sqrt(2), self.speed / math.sqrt(2))
                self.idle = False
            if self.attackMode == False:
                self.counterImages += self.imageRate
                self.imageCurrentList = self.playerWalkingRigthCoor
                if self.counterImages > len(self.imageCurrentList) - 2:
                    self.counterImages = 0

        if keys[pygame.K_w] and not (keys[pygame.K_s] or keys[pygame.K_d] or keys[pygame.K_a]) \
                and "down" not in self.wallsCollided:
            self.playerRect.move_ip(0, -self.speed)
            self.idle = False
            if self.attackMode == False:
                self.counterImages += self.imageRate
                self.imageCurrentList = self.playerWalkingUpCoor
                if self.counterImages > len(self.imageCurrentList) - 2:
                    self.counterImages = 0

        if keys[pygame.K_s] and not (keys[pygame.K_w] or keys[pygame.K_d] or keys[pygame.K_a]) \
                and "up" not in self.wallsCollided:
            self.playerRect.move_ip(0, self.speed)
            self.idle = False
            if self.attackMode == False:

                self.counterImages += self.imageRate
                self.imageCurrentList = self.playerWalkingDownCoor
                if self.counterImages > len(self.imageCurrentList) - 2:
                    self.counterImages = 0

        if (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]) == False:
            if self.attackMode == True:
                self.idle = True
            else:
                self.idle = True
                self.imageCurrentList = self.playerIdleCoor
                self.counterImages = 0

    def checkWalls(self, walls):
        self.wallsCollided = []
        wallsIndexs = self.playerRect.collidelistall(walls)

        for wall in wallsIndexs:
            playerRight = self.playerRect.x + self.playerRect.width
            playerLeft = self.playerRect.x
            playerTop = self.playerRect.y + 30
            playerBottom = self.playerRect.y + self.playerRect.height

            wallRight = walls[wall].x + walls[wall].width
            wallLeft = walls[wall].x
            wallTop = walls[wall].y
            wallBottom = walls[wall].y + walls[wall].height
            if playerTop - 5 <= wallBottom and wallBottom - 5 <= playerTop:
                print("down")
                self.wallsCollided.append("down")
            if playerBottom + 5 >= wallTop and wallTop + 5 >= playerBottom:
                print("up")
                self.wallsCollided.append("up")
            if playerLeft - 5 <= wallRight and wallRight - 5 <= playerLeft:
                print("right")
                self.wallsCollided.append("right")
            if playerRight + 5 >= wallLeft and wallLeft + 5 >= playerRight:
                print("left")
                self.wallsCollided.append("left")

        # return "none"

    def drawPlayer(self, screen):
        if self.attackMode:
            self.spriteSheet = self.spriteSheet = pygame.image.load(
                self.spriteSheetImages[playerProgress["playerOutfit"]][playerProgress["playerGun"]]).convert_alpha()
            screen.blit(self.blackSpot,
                        pygame.rect.Rect(self.playerRect.x + (self.playerRect.w / 2) - self.blackSpotRect.w / 2,
                                         self.playerRect.y + (self.playerRect.h / 2) - self.blackSpotRect.h / 2,
                                         self.blackSpotRect.w, self.blackSpotRect.h))
        else:
            self.spriteSheet = self.spriteSheet = pygame.image.load(
                self.spriteSheetImages[playerProgress["playerOutfit"]][0]).convert_alpha()
        for bullet in self.bulletList:
            bullet.drawBullet(screen)
        rect = pygame.Rect((self.imageCurrentList[math.floor(self.counterImages)][0][0],
                            self.imageCurrentList[math.floor(self.counterImages)][0][1],
                            self.imageCurrentList[math.floor(self.counterImages)][1][0],
                            self.imageCurrentList[math.floor(self.counterImages)][1][1]))
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.spriteSheet, (0, 0), rect)
        if self.imageCurrentList == self.playerWalkingRigthCoorShooting or \
                self.imageCurrentList == self.playerWalkingLeftCoorShooting or \
                self.imageCurrentList == [self.playerWalkingRigthCoorShooting[0]] or \
                self.imageCurrentList == [self.playerWalkingLeftCoorShooting[0]]:
            screen.blit(pygame.transform.scale(image, (48, 78)), self.playerRect)

        else:
            screen.blit(pygame.transform.scale(image, (36, 78)), self.playerRect)

    def drawLifes(self, screen):
        for heart in range(playerProgress["playerLife"]):
            rect = self.heartImage.get_rect()
            rect.x = widthS - (rect.w * (heart + 1)) - (5 * (heart + 1))
            rect.y = heightS - rect.h - 4
            screen.blit(self.heartImage, rect)

    def lowerLife(self):
        playerProgress["playerLife"] = playerProgress["playerLife"] - 1

    def drawCoins(self, screen):
        rect = self.coinImage.get_rect()
        rect.x = 18
        rect.y = 18
        screen.blit(self.coinImage, rect)
        coinsText = scoreText(False, 68, 38, str(playerProgress["playerCoins"]), 28, (242, 242, 242))
        coinsText[1].x = rect.x + rect.w + 10
        screen.blit(coinsText[0], coinsText[1])


class Level1:
    def __init__(self):
        self.previousPlayerProgress = playerProgress.copy()
        self.houseColorList = levelProgress["mainPatio"]
        self.wallsList = []
        self.houseList = []
        self.enemysList = []
        self.interactableObjectsList = []
        self.decorationsList = []
        self.bg_image = pygame.image.load("pictures/bgGame0.png").convert()
        self.walls()
        self.decorations()
        self.buildings()
        self.player = Player(30, 60, 500, 400, self.getBoundaries())
        self.borderWallsImage = None
        self.enemyWave = None

        self.doorsInfo = []

        self.player.attackMode = False

        self.enemys()
        self.interactableObjects()
        self.interactable = None

    def walls(self):
        # Bottom Left Corner
        wall1 = Wall("pictures/barrierHorizontalHookLeft160x30Game.png", 160, 30, 0, 490)
        wall1_5 = Wall("pictures/barrierHorizontalHookRight180x30Game.png", 180, 30, 230, 490)
        wall2 = Wall("pictures/barrierVertical10x350.png", 10, 350, 410, 490)

        # Bottom Right Corner
        wall4 = Wall("pictures/barrierHorizontalHookLeft160x30Game.png", 160, 30, 590, 490)
        wall4_5 = Wall("pictures/barrierHorizontalHookRight180x30Game.png", 180, 30, 840, 490)
        wall5 = Wall("pictures/barrierVertical10x350.png", 10, 350, 580, 490)

        # Top Left Corner
        wall7 = Wall("pictures/barrierHorizontalHookLeft160x30Game.png", 160, 30, 0, 320)
        wall7_5 = Wall("pictures/barrierHorizontalHookRight180x30Game.png", 180, 30, 230, 320)
        wall8 = Wall("pictures/barrierVertical10x350.png", 10, 350, 410, 0)

        # Top Right Corner
        wall10 = Wall("pictures/barrierHorizontalHookLeft160x30Game.png", 160, 30, 590, 320)
        wall10_5 = Wall("pictures/barrierHorizontalHookRight180x30Game.png", 180, 30, 840, 320)
        wall11 = Wall("pictures/barrierVertical10x350.png", 10, 350, 580, 0)

        self.wallsList = [wall1, wall1_5, wall2, wall4, wall4_5, wall5, wall7, wall7_5, wall8, wall10, wall10_5, wall11]

        return self.wallsList

    def buildings(self):
        def interactableLevel1():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableLucaHouse():
            door([0, 0, Level3, 2, None])
            self.interactable = None

        def interactableDisappear():
            self.interactable = None

        def house1Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLucaHouse], ["No", interactableDisappear]])

        def house2Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])
            if self.houseColorList[0] != "haunted":
                self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                                 "You have already saved Miranda's House!",
                                                 [["Ok", interactableDisappear]])

        def house3Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])
            if self.houseColorList[1] != "haunted":
                self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                                 "You have already saved Luca's House!",
                                                 [["Ok", interactableDisappear]])

        def house4Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])
            if self.houseColorList[2] != "haunted":
                self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                                 "You have already saved Miranda's House!",
                                                 [["Ok", interactableDisappear]])

        house1 = House(60, -50, 1, "blue", house1Func)
        house2 = House(660, -50, 1, self.houseColorList[0], house2Func)
        house3 = House(60, 550, 2, self.houseColorList[1], house3Func)
        house4 = House(660, 550, 2, self.houseColorList[2], house4Func)
        self.houseList = [house1, house2, house3, house4]

        return self.houseList

    def decorations(self):
        coordinates = [[[6, 13], [19, 8]], [[6, 45], [19, 8]]]
        plant0 = Decorations(10, 110, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant1 = Decorations(30, 60, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant2 = Decorations(20, 220, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant3 = Decorations(15, 140, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant4 = Decorations(27, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant5 = Decorations(38, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant6 = Decorations(130, 250, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant7 = Decorations(150, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant8 = Decorations(170, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant9 = Decorations(190, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant10 = Decorations(210, 270, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant11 = Decorations(230, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant12 = Decorations(250, 300, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant13 = Decorations(270, 230, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant14 = Decorations(290, 120, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant15 = Decorations(310, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant16 = Decorations(330, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant17 = Decorations(350, 180, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant18 = Decorations(370, 240, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant19 = Decorations(240, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant20 = Decorations(280, 130, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        self.decorationsList = [plant0, plant1, plant2, plant3, plant4,
                                plant5, plant6, plant7, plant8, plant9,
                                plant10, plant11, plant12, plant13, plant14,
                                plant15, plant16, plant17, plant18, plant19,
                                plant20
                                ]

    def enemys(self):
        # enemy1 = Enemy("pictures/PlayerSpritesheet.png",
        #                30, 60, 700, 700,
        #                self.player.playerRect,
        #                self.player.bulletList, speed=4)

        self.enemysList = []
        return self.enemysList

    def getBoundaries(self):
        return self.wallsList + self.houseList

    def drawDecor(self, screen):
        for decor in self.decorationsList:
            decor.drawDecorations(screen)

    def drawWallsBehind(self, screen, playerY):
        for wall in self.wallsList:
            if playerY >= wall.wallRect.y:
                wall.drawWall(screen)

    def drawWallsFront(self, screen, playerY):
        for wall in self.wallsList:
            if playerY < wall.wallRect.y:
                wall.drawWall(screen)

    def drawHousesBehind(self, screen, playerY):
        for house in self.houseList:
            if playerY >= house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawHousesFront(self, screen, playerY):
        for house in self.houseList:
            if playerY < house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawInteractable(self, screen):
        if self.interactable != None:
            self.interactable.drawInteractable(screen)

    def drawMoveEnemy(self, screen):
        for enemy in self.enemysList:
            if enemy.alive == True:
                enemy.move()
                enemy.drawEnemy(screen)
            else:
                self.enemysList.remove(enemy)

    def drawBackGround(self, screen, widthS, heightS):
        screen.blit(pygame.transform.scale(self.bg_image, (widthS, heightS)), (0, 0))

    def interactableObjects(self):
        def interactableLevel1():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableLucaHouse():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableDisappear():
            self.interactable = None

        def object1Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Nothing :)",
                                             [["No", interactableDisappear],
                                              ["No", interactableDisappear],
                                              ["No", interactableDisappear],
                                              ["No", interactableDisappear],
                                              ["No", interactableDisappear],
                                              ["No", interactableDisappear]])

        def object2Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def object3Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def object4Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        object1 = InteractableObject(700, 360, 40, 40, False, object1Func)
        # object2 = House(660, -50, 1, self.houseColorList[0], object2Func)
        # object3 = House(60, 550, 2, self.houseColorList[1], object3Func)
        # object4 = House(660, 550, 2, self.houseColorList[2], object4Func)
        self.interactableObjectsList = [object1]  # , object2, object3, object4]

        return self.interactableObjectsList

    def drawInteractableObjects(self, screen):
        for object in self.interactableObjectsList:
            object.drawHouse(screen, self.player)


class Wall:
    def __init__(self, image, width, height, xPOS, yPOS, angle=0):
        if image is None:
            self.wallRect = pygame.rect.Rect(xPOS, yPOS, width, height)
            self.image = pygame.Surface(pygame.Rect(self.wallRect).size, pygame.SRCALPHA)
            # pygame.draw.rect(transparentSurface, (0, 0, 0, 0), transparentSurface.get_rect())
            # screen.blit(self.image, self.wallRect)
        else:
            self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(image).convert_alpha(),
                                                                        (width, height)), angle)
            self.wallRect = self.image.get_rect()
            self.wallRect.x = xPOS
            self.wallRect.y = yPOS

    def drawWall(self, screen):

        screen.blit(self.image, self.wallRect)

    def getRect(self):
        return self.wallRect


class Decorations:
    def __init__(self, xPos, yPos, width, height, coordinates, spritesheet, imageRate=0.05):
        self.images = coordinates
        self.decorRect = pygame.rect.Rect((xPos, yPos, width, height))
        self.spriteSheet = pygame.image.load(spritesheet).convert_alpha()
        self.counterImages = 0
        self.imageRate = imageRate

    def animateDecor(self):
        self.counterImages += self.imageRate
        if self.counterImages > len(self.images):
            self.counterImages = 0

    def drawDecorations(self, screen):
        self.animateDecor()

        rect = pygame.Rect((self.images[math.floor(self.counterImages)][0][0],
                            self.images[math.floor(self.counterImages)][0][1],
                            self.images[math.floor(self.counterImages)][1][0],
                            self.images[math.floor(self.counterImages)][1][1]))
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.spriteSheet, (0, 0), rect)

        screen.blit(pygame.transform.scale(image, (self.decorRect.w, self.decorRect.h)), self.decorRect)


class House:
    def __init__(self, xPos, yPos, houseType, color, interactable):
        self.xPos = xPos
        self.yPos = yPos
        self.player = None
        colors = ["red", "blue", "yellow", "green", "haunted"]
        # red, blue, yellow, orange, haunted,
        types = [[["pictures/HouseGameRed.png"], ["pictures/", "pictures/"], ["pictures/", "pictures/", "pictures/"]],
                 [["pictures/HouseGame1.png"], ["pictures/", "pictures/"], ["pictures/", "pictures/", "pictures/"]],
                 [["pictures/HouseGameBackwardsYellow.png"], ["pictures/", "pictures/"],
                  ["pictures/", "pictures/", "pictures/"]],
                 [["pictures/HouseGameBackwardsGreen.png"], ["pictures/", "pictures/"],
                  ["pictures/", "pictures/", "pictures/"]],
                 [["pictures/hauntedHouseForward.png"], ["pictures/hauntedHouseGameBackwards.png"],
                  ["pictures/", "pictures/", "pictures/"]],
                 ]
        self.width = 270
        self.height = 270

        self.houseType = houseType
        self.houseInfo = types[colors.index(color)][houseType - 1]
        self.houseImage = None
        self.houseRect = None
        self.interactableRect = None
        self.interactable = interactable
        self.houseSetUp()
        self.interactableDisplayed = False

    def houseSetUp(self):
        if self.houseType is not None:
            self.houseImage = pygame.transform.scale(pygame.image.load(self.houseInfo[0]).convert_alpha(),
                                                     (self.width, self.height))
            self.houseRect = self.houseImage.get_rect()
            self.houseRect.x = self.xPos
            self.houseRect.y = self.yPos

        if self.houseType == 2:
            pass

        if self.houseType == 3:
            pass

    def drawHouse(self, screen, player):
        self.player = player
        if self.houseType is not None:
            sizeFromOrigin = 30
            self.interactableRect = pygame.rect.Rect(self.houseRect.x - sizeFromOrigin,
                                                     self.houseRect.y - sizeFromOrigin,
                                                     self.houseRect.w + sizeFromOrigin * 2,
                                                     self.houseRect.h + sizeFromOrigin * 2)

            transparentSurface = pygame.Surface(pygame.Rect(self.interactableRect).size, pygame.SRCALPHA)
            # pygame.draw.rect(transparentSurface, (0, 0, 0, 0), transparentSurface.get_rect())
            screen.blit(transparentSurface, self.interactableRect)

            # pygame.draw.rect(screen, (0, 0, 0, 128), self.interactableRect)
            screen.blit(self.houseImage, self.houseRect)

            if self.player.playerRect.colliderect(self.interactableRect) == True:
                if self.interactableDisplayed == False:
                    self.interactable()
                    self.interactableDisplayed = True
            else:
                self.interactableDisplayed = False

        if self.houseType == 2:
            pass

        if self.houseType == 3:
            pass

    def getRect(self):
        return self.houseRect


class InteractableObject:
    def __init__(self, xPos, yPos, width, height, image, interactable, sizeFromOrigin=5):
        self.xPos = xPos
        self.yPos = yPos
        self.player = None
        self.width = width
        self.height = height
        self.sizeFromOrigin = sizeFromOrigin
        if image == False:
            image = "pictures/coinGame.png"
            self.interactableObjectImage = pygame.transform.scale(pygame.image.load(image).convert_alpha(),
                                                                  (self.width, self.height))
            self.interactableObjectImage.set_alpha(0)
        else:
            self.interactableObjectImage = pygame.transform.scale(pygame.image.load(image).convert_alpha(),
                                                                  (self.width, self.height))

        self.interactableObjectRect = self.interactableObjectImage.get_rect()
        self.interactableObjectRect.x = self.xPos
        self.interactableObjectRect.y = self.yPos
        self.interactableRect = None
        self.interactable = interactable
        self.interactableDisplayed = False

    def drawHouse(self, screen, player):
        self.player = player

        self.interactableRect = pygame.rect.Rect(self.interactableObjectRect.x - self.sizeFromOrigin,
                                                 self.interactableObjectRect.y - self.sizeFromOrigin,
                                                 self.interactableObjectRect.w + self.sizeFromOrigin * 2,
                                                 self.interactableObjectRect.h + self.sizeFromOrigin * 2)

        transparentSurface = pygame.Surface(pygame.Rect(self.interactableRect).size, pygame.SRCALPHA)
        screen.blit(transparentSurface, self.interactableRect)
        screen.blit(self.interactableObjectImage, self.interactableObjectRect)

        if self.player.playerRect.colliderect(self.interactableRect) == True:
            if self.interactableDisplayed == False:
                self.interactable()
                self.interactableDisplayed = True
        else:
            self.interactableDisplayed = False

    def getRect(self):
        return self.interactableObjectRect


class Interactable:
    def __init__(self, width, height, xPOS, yPOS, textMessage, buttons):
        self.separationButtons = 5
        self.buttonHeight = 50
        self.buttonWidth = math.floor((width - self.separationButtons * 2) / 2)
        self.image = pygame.transform.scale(pygame.image.load("pictures/InteractableGame.png").convert_alpha(),
                                            (width, height))
        self.imageButton = pygame.transform.scale(
            pygame.image.load("pictures/InteractableButtonGame.png").convert_alpha(),
            (self.buttonWidth, self.buttonHeight))
        self.interactableRect = self.image.get_rect()
        self.interactableRect.x = xPOS
        self.interactableRect.y = yPOS
        self.textMessage = textMessage
        self.buttonsInfo = buttons  # [["Button Message", "Function"], ["OK", "func"]] Max 4
        self.buttonsKeys = [pygame.K_h, pygame.K_j, pygame.K_n, pygame.K_m, pygame.K_k, pygame.K_l]
        self.buttonsKeysText = ["(h)", "(j)", "(n)", "(m)", "(k)", "(l)"]
        self.button1 = None
        self.button2 = None
        self.button3 = None
        self.button4 = None
        self.button5 = None
        self.button6 = None
        self.buttonsList = [self.button1, self.button2, self.button3, self.button4, self.button5, self.button6]

        self.buttonPositions = [[xPOS, yPOS + height + self.separationButtons],
                                [xPOS + self.buttonWidth + self.separationButtons,
                                 yPOS + height + self.separationButtons],
                                [xPOS, yPOS + height + self.separationButtons * 2 + self.buttonHeight],
                                [xPOS + self.buttonWidth + self.separationButtons,
                                 yPOS + height + self.separationButtons * 2 + self.buttonHeight],
                                [xPOS, yPOS + height + self.separationButtons * 3 + self.buttonHeight * 2],
                                [xPOS + self.buttonWidth + self.separationButtons,
                                 yPOS + height + self.separationButtons * 3 + self.buttonHeight * 2]]

        for button in range(0, len(self.buttonsInfo)):
            self.buttonsList[button] = self.imageButton.get_rect()
            self.buttonsList[button].x = self.buttonPositions[button][0]
            self.buttonsList[button].y = self.buttonPositions[button][1]

    def drawInteractable(self, screen):

        screen.blit(self.image, self.interactableRect)

        if len(self.textMessage) > 30:

            textAll = self.textMessage.split(" ")
            lengthTM = int(math.ceil(len(textAll)) / 2)
            text1 = ' '.join(textAll[:lengthTM])
            text2 = ' '.join(textAll[lengthTM:])
            interactableText1 = scoreText(False,
                                          self.interactableRect.x + (self.interactableRect.w / 2),
                                          self.interactableRect.y + (self.interactableRect.h / 2) - 20,
                                          text1, 28, (67, 63, 59))
            interactableText2 = scoreText(False,
                                          self.interactableRect.x + (self.interactableRect.w / 2),
                                          self.interactableRect.y + (self.interactableRect.h / 2) + 20,
                                          text2, 28, (67, 63, 59))

            screen.blit(interactableText1[0], interactableText1[1])
            screen.blit(interactableText2[0], interactableText2[1])

        else:
            interactableText = scoreText(False,
                                         self.interactableRect.x + (self.interactableRect.w / 2),
                                         self.interactableRect.y + (self.interactableRect.h / 2) - 20,
                                         self.textMessage, 28, (67, 63, 59))

            screen.blit(interactableText[0], interactableText[1])

        keys = pygame.key.get_pressed()

        if len(self.buttonsInfo) == 1:
            self.buttonsList[0].x = self.interactableRect.x + (self.interactableRect.w / 2) - (
                    self.buttonsList[0].w / 2)
            self.buttonsList[0].y = self.interactableRect.y + self.interactableRect.h + self.separationButtons

        for button in range(0, len(self.buttonsInfo)):
            if keys[self.buttonsKeys[button]]:
                self.buttonsInfo[button][1]()

            buttonTextMessage = self.buttonsInfo[button][0] + " " + self.buttonsKeysText[button]

            buttonText = scoreText(False,
                                   self.buttonsList[button].x + (self.buttonWidth / 2),
                                   self.buttonsList[button].y + (self.buttonHeight / 2),
                                   buttonTextMessage, 28, (255, 240, 225))
            screen.blit(self.imageButton, self.buttonsList[button])
            screen.blit(buttonText[0], buttonText[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, width, height, xPOS, yPOS, playerRect, bulletsList, enemyList=None, speed=4,
                 lowerLife=None):
        super().__init__()
        self.speed = speed
        self.lowerPlayerLife = lowerLife

        self.bulletsList = bulletsList

        self.playerEnemyRect = playerRect

        self.enemyList = []

        if enemyList is not None:
            for e in enemyList:
                self.enemyList.append(e.enemyRect)

        self.enemyRect = pygame.rect.Rect((xPOS, yPOS, width, height))

        self.spriteSheet = pygame.image.load(image).convert_alpha()
        #   16 66 116 166 216
        # 5
        # 50
        # 105
        # 155
        # 205
        self.enemyIdleCoor = [[[16, 5], [50, 48]]]

        self.enemyWalkingUpCoor = [
            [[66, 5], [18, 39]],
            [[116, 5], [18, 39]],
            [[166, 5], [18, 39]],
            [[116, 5], [18, 39]],
            [[66, 5], [18, 39]],
            [[216, 5], [18, 39]],
            [[16, 55], [18, 39]],
            [[216, 5], [18, 39]]]

        self.enemyWalkingDownCoor = [
            [[66, 55], [18, 39]],
            [[116, 55], [18, 39]],
            [[166, 55], [18, 39]],
            [[116, 55], [18, 39]],
            [[66, 55], [18, 39]],
            [[216, 55], [18, 39]],
            [[16, 105], [18, 39]],
            [[216, 55], [18, 39]]]

        self.enemyWalkingRigthCoor = [[[16, 94], [50, 48]]]

        self.enemyWalkingLeftCoor = [[[16, 14], [50, 48]]]

        self.counterImages = 0
        self.imageRate = 0.3
        self.imageCurrentList = self.enemyWalkingRigthCoor

        self.wallsCollided = []

        self.alive = True

    def move(self):
        bulletRectList = []
        for bullet in self.bulletsList:
            bulletRectList.append(bullet.bulletRect)

        if len(bulletRectList) != 0:
            bulletCollide = self.enemyRect.collidelist(bulletRectList)
            if bulletCollide != -1:
                self.alive = False
                playerProgress["playerCoins"] += 10
                self.bulletsList.pop(bulletCollide)

        xDistance = self.playerEnemyRect.x - self.enemyRect.x
        yDistance = self.playerEnemyRect.y - self.enemyRect.y
        c = math.sqrt((xDistance ** 2) + (yDistance ** 2)) / self.speed
        if xDistance > 0:
            self.imageCurrentList = self.enemyWalkingLeftCoor
        else:
            self.imageCurrentList = self.enemyWalkingRigthCoor

        if len(self.enemyList) > 0:
            self.checkWalls(self.enemyList)

        if c != 0:
            if "right" in self.wallsCollided:
                if xDistance / c < 0:
                    if "down" in self.wallsCollided:
                        if yDistance / c < 0:
                            self.enemyRect.move_ip(-xDistance / c, -yDistance / c)
                    elif "up" in self.wallsCollided:
                        if xDistance / c >= 0:
                            self.enemyRect.move_ip(-xDistance / c, -yDistance / c)
                    else:
                        self.enemyRect.move_ip(-xDistance / c, yDistance / c)

            if "left" in self.wallsCollided:
                if xDistance / c >= 0:
                    if "down" in self.wallsCollided:
                        if yDistance / c < 0:
                            self.enemyRect.move_ip(-xDistance / c, -yDistance / c)
                    elif "up" in self.wallsCollided:
                        if xDistance / c >= 0:
                            self.enemyRect.move_ip(-xDistance / c, -yDistance / c)
                    else:
                        self.enemyRect.move_ip(-xDistance / c, yDistance / c)

            if "down" in self.wallsCollided:
                if yDistance / c < 0:
                    self.enemyRect.move_ip(xDistance / c, -yDistance / c)

            if "up" in self.wallsCollided:
                if xDistance / c >= 0:
                    self.enemyRect.move_ip(xDistance / c, -yDistance / c)

            if len(self.wallsCollided) == 0:
                self.enemyRect.move_ip(xDistance / c, yDistance / c)

        if self.enemyRect.colliderect(self.playerEnemyRect):
            if self.lowerPlayerLife is not None:
                self.lowerPlayerLife()
            self.alive = False

    def checkWalls(self, walls):
        self.wallsCollided = []
        wallsIndexs = self.enemyRect.collidelistall(walls)

        for wall in wallsIndexs:
            print("Walls x: " + str(walls[wall].x + walls[wall].width))
            print("PLayer x: " + str(self.enemyRect.x))
            playerRight = self.enemyRect.x + self.enemyRect.width
            playerLeft = self.enemyRect.x
            playerTop = self.enemyRect.y
            playerBottom = self.enemyRect.y + self.enemyRect.height

            wallRight = walls[wall].x + walls[wall].width
            wallLeft = walls[wall].x
            wallTop = walls[wall].y
            wallBottom = walls[wall].y + walls[wall].height
            if playerTop - self.speed + 1 <= wallBottom and wallBottom - self.speed + 1 <= playerTop:
                print("down")
                self.wallsCollided.append("down")
            if playerBottom + self.speed + 1 >= wallTop and wallTop + self.speed + 1 >= playerBottom:
                print("up")
                self.wallsCollided.append("up")
            if playerLeft - self.speed + 1 <= wallRight and wallRight - self.speed + 1 <= playerLeft:
                print("right")
                self.wallsCollided.append("right")
            if playerRight + self.speed + 1 >= wallLeft and wallLeft + self.speed + 1 >= playerRight:
                print("left")
                self.wallsCollided.append("left")

        # return "none"

    def drawEnemy(self, screen):
        rect = pygame.Rect((self.imageCurrentList[math.floor(self.counterImages)][0][0],
                            self.imageCurrentList[math.floor(self.counterImages)][0][1],
                            self.imageCurrentList[math.floor(self.counterImages)][1][0],
                            self.imageCurrentList[math.floor(self.counterImages)][1][1]))
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.spriteSheet, (0, 0), rect)

        screen.blit(pygame.transform.scale(image, (self.enemyRect.w, self.enemyRect.h)), self.enemyRect)


class Bullet:
    def __init__(self, width, height, playerRect, speed=4, image=None):
        super().__init__()
        self.speed = speed
        self.image = image

        self.playerBulletRect = playerRect

        self.bulletRect = pygame.rect.Rect(
            (playerRect.x + (playerRect.w / 2), playerRect.y + (playerRect.h / 2), width, height))

        self.xDir = 0

        self.yDir = 0

    def setUpBullet(self):

        mousePos = pygame.mouse.get_pos()
        xDistance = mousePos[0] - self.bulletRect.x
        yDistance = mousePos[1] - self.bulletRect.y
        c = math.sqrt((xDistance ** 2) + (yDistance ** 2)) / self.speed
        if c != 0:
            self.xDir = xDistance / c
            self.yDir = yDistance / c

    def move(self):
        self.bulletRect.move_ip(self.xDir, self.yDir)

        if self.bulletRect.colliderect(self.playerBulletRect):
            # lower life of enemy
            pass

    def drawBullet(self, screen):
        if self.image == None:
            pygame.draw.rect(screen, (0, 0, 0), self.bulletRect, 0, 50)
        # screen.blit(pygame.transform.scale(image, (36, 78)), self.enemyRect)


class Level2:
    def __init__(self):
        self.previousPlayerProgress = playerProgress.copy()
        self.wallsList = []
        self.houseList = []
        self.enemysList = []
        self.interactableObjectsList = []
        self.decorationsList = []
        self.bg_image = pygame.image.load("pictures/Checkered-Floor400x320.png").convert_alpha()
        self.bg_image.set_alpha(128)
        self.borderWallsImage = pygame.image.load("pictures/wallsHauntedHouse2.png").convert_alpha()
        self.borderWallsImageAfter = pygame.image.load("pictures/insideSavedHouse.png").convert_alpha()
        self.walls()
        self.decorations()
        self.buildings()
        self.player = Player(30, 60, 500, 400, self.getBoundaries())

        self.doorsInfo = [pygame.rect.Rect(430, 800, 135, 50), self.player.playerRect, Level1, 1]
        self.enemyWaveList = [self.enemysThirdWave, self.enemysSecondWave, self.enemys]

        self.player.attackMode = True

        self.enemyWave = len(self.enemyWaveList) - 1

        self.enemys()
        self.interactableObjects()
        self.interactable = None

    def walls(self):
        # Border Walls
        wall12 = Wall(None, width=10, height=800, xPOS=50 - 10, yPOS=0)
        wall13 = Wall(None, width=10, height=800, xPOS=945, yPOS=0)
        wall14 = Wall(None, width=1000, height=70, xPOS=0, yPOS=0)

        wall15 = Wall(None, width=1000, height=100, xPOS=0, yPOS=736)

        # wall15 = Wall(None, width=430, height=100, xPOS=0, yPOS=736)
        # wall16 = Wall(None, width=435, height=100, xPOS=565, yPOS=736)

        self.wallsList = [wall12, wall13, wall14, wall15]

        # self.wallsList = [wall1, wall1_5, wall2, wall4, wall4_5, wall5, wall7, wall7_5, wall8, wall10, wall10_5, wall11]

        return self.wallsList

    def buildings(self):
        def interactableFunc1():
            self.interactable = None

        def house1Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableFunc1], ["No", interactableFunc1]])

        def house2Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableFunc1], ["No", interactableFunc1]])

        def house3Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableFunc1], ["No", interactableFunc1]])

        def house4Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableFunc1], ["No", interactableFunc1]])

        house1 = House(60, -50, 1, "blue", house1Func)
        house2 = House(660, -50, 1, "red", house2Func)
        house3 = House(60, 550, 1, "yellow", house3Func)
        house4 = House(660, 550, 1, "green", house4Func)
        # self.houseList = [house1, house2, house3, house4]

        return self.houseList

    def decorations(self):
        coordinates = [[[6, 13], [19, 8]], [[6, 45], [19, 8]]]
        plant0 = Decorations(10, 110, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant1 = Decorations(30, 60, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant2 = Decorations(20, 220, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant3 = Decorations(15, 140, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant4 = Decorations(27, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant5 = Decorations(38, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant6 = Decorations(130, 250, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant7 = Decorations(150, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant8 = Decorations(170, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant9 = Decorations(190, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant10 = Decorations(210, 270, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant11 = Decorations(230, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant12 = Decorations(250, 300, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant13 = Decorations(270, 230, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        plant14 = Decorations(290, 120, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant15 = Decorations(310, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant16 = Decorations(330, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant17 = Decorations(350, 180, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant18 = Decorations(370, 240, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant19 = Decorations(240, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        plant20 = Decorations(280, 130, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        # self.decorationsList = [plant0, plant1, plant2, plant3, plant4,
        #                         plant5, plant6, plant7, plant8, plant9,
        #                         plant10, plant11, plant12, plant13, plant14,
        #                         plant15, plant16, plant17, plant18, plant19,
        #                         plant20
        #                         ]

    def enemys(self):
        enemy1 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 700, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy2 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 700, 500,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy3 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 700, 300,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy1.enemyList = [enemy2.enemyRect, enemy3.enemyRect]
        enemy2.enemyList = [enemy1.enemyRect, enemy3.enemyRect]
        enemy3.enemyList = [enemy2.enemyRect, enemy1.enemyRect]

        self.enemysList = [enemy1, enemy2, enemy3]
        return self.enemysList

    def enemysSecondWave(self):
        enemy1 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 700, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy2 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 700, 500,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy3 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 700, 300,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=3, lowerLife=self.player.lowerLife)

        enemy4 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 600, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=3, lowerLife=self.player.lowerLife)

        enemy5 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 400, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy6 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 200, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy1.enemyList = [enemy2.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy5.enemyRect, enemy6.enemyRect]
        enemy2.enemyList = [enemy1.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy5.enemyRect, enemy6.enemyRect]
        enemy3.enemyList = [enemy2.enemyRect, enemy1.enemyRect, enemy4.enemyRect, enemy5.enemyRect, enemy6.enemyRect]
        enemy4.enemyList = [enemy2.enemyRect, enemy3.enemyRect, enemy1.enemyRect, enemy5.enemyRect, enemy6.enemyRect]
        enemy5.enemyList = [enemy1.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy1.enemyRect, enemy6.enemyRect]
        enemy6.enemyList = [enemy2.enemyRect, enemy1.enemyRect, enemy4.enemyRect, enemy5.enemyRect, enemy1.enemyRect]

        self.enemysList = [enemy1, enemy2, enemy3, enemy4, enemy5, enemy6]
        return self.enemysList

    def enemysThirdWave(self):
        enemy1 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 700, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy2 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 700, 500,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=2, lowerLife=self.player.lowerLife)

        enemy3 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 700, 300,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=3, lowerLife=self.player.lowerLife)

        enemy4 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 600, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=3, lowerLife=self.player.lowerLife)

        enemy5 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 400, 700,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy6 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 200, 100,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)
        enemy7 = Enemy("pictures/ghostsCrazyGame.png",
                       100, 96, 600, 100,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=3, lowerLife=self.player.lowerLife)

        enemy8 = Enemy("pictures/ghostsNormalGame.png",
                       100, 96, 400, 100,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy9 = Enemy("pictures/ghostsWhiteGame.png",
                       100, 96, 100, 100,
                       self.player.playerRect,
                       self.player.bulletList, enemyList=[], speed=4, lowerLife=self.player.lowerLife)

        enemy1.enemyList = [enemy2.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy5.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy2.enemyList = [enemy1.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy5.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy3.enemyList = [enemy2.enemyRect, enemy1.enemyRect, enemy4.enemyRect, enemy5.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy4.enemyList = [enemy2.enemyRect, enemy3.enemyRect, enemy1.enemyRect, enemy5.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy5.enemyList = [enemy1.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy2.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy6.enemyList = [enemy2.enemyRect, enemy1.enemyRect, enemy4.enemyRect, enemy5.enemyRect,
                            enemy3.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy7.enemyList = [enemy2.enemyRect, enemy3.enemyRect, enemy1.enemyRect, enemy5.enemyRect,
                            enemy6.enemyRect, enemy4.enemyRect, enemy8.enemyRect, enemy9.enemyRect]
        enemy8.enemyList = [enemy1.enemyRect, enemy3.enemyRect, enemy4.enemyRect, enemy2.enemyRect,
                            enemy6.enemyRect, enemy7.enemyRect, enemy5.enemyRect, enemy9.enemyRect]
        enemy9.enemyList = [enemy2.enemyRect, enemy1.enemyRect, enemy4.enemyRect, enemy5.enemyRect,
                            enemy1.enemyRect, enemy7.enemyRect, enemy8.enemyRect, enemy6.enemyRect]

        self.enemysList = [enemy1, enemy2, enemy3, enemy4, enemy5, enemy6, enemy7, enemy8, enemy9]
        return self.enemysList

    def getBoundaries(self):
        return self.wallsList + self.houseList

    def drawDecor(self, screen):
        for decor in self.decorationsList:
            decor.drawDecorations(screen)

    def drawWallsBehind(self, screen, playerY):
        for wall in self.wallsList:
            if playerY >= wall.wallRect.y:
                wall.drawWall(screen)

    def drawWallsFront(self, screen, playerY):
        for wall in self.wallsList:
            if playerY < wall.wallRect.y:
                wall.drawWall(screen)

        self.drawLevelInfo(screen)

    def drawLevelInfo(self, screen):
        if self.enemyWave >= -1:
            waves = scoreText(False, 120, 785,
                              "Waves left " + str(self.enemyWave + 1) + "/" + str(len(self.enemyWaveList)),
                              28, (242, 242, 242))
            screen.blit(waves[0], waves[1])

    def drawHousesBehind(self, screen, playerY):
        for house in self.houseList:
            if playerY >= house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawHousesFront(self, screen, playerY):
        for house in self.houseList:
            if playerY < house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawInteractable(self, screen):
        if self.interactable != None:
            self.interactable.drawInteractable(screen)

    def drawMoveEnemy(self, screen):
        for enemy in self.enemysList:
            if enemy.alive == True:
                enemy.move()
                enemy.drawEnemy(screen)
            else:
                self.enemysList.remove(enemy)
                enemy.enemyRect.x = -500

    def drawBackGround(self, screen, widthS, heightS):
        pygame.draw.rect(screen, (242, 242, 242), pygame.rect.Rect(0, 0, widthS, heightS))
        screen.blit(pygame.transform.scale(self.bg_image, (widthS, heightS)), (0, 0))
        if self.borderWallsImage is not None:
            screen.blit(pygame.transform.scale(self.borderWallsImageAfter, (widthS, heightS)), (0, 0))
            screen.blit(pygame.transform.scale(self.borderWallsImage, (widthS, heightS)), (0, 0))

    def interactableObjects(self):
        def interactableLevel1():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableLucaHouse():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableDisappear():
            self.interactable = None

        def object1Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLucaHouse], ["No", interactableDisappear]])

        def object2Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def object3Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def object4Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        # object1 = House(60, -50, 1, "blue", object1Func)
        # object2 = House(660, -50, 1, self.houseColorList[0], object2Func)
        # object3 = House(60, 550, 2, self.houseColorList[1], object3Func)
        # object4 = House(660, 550, 2, self.houseColorList[2], object4Func)
        # self.interactableObjectsList = [object1, object2, object3, object4]

        return self.interactableObjectsList

    def drawInteractableObjects(self, screen):
        for object in self.interactableObjectsList:
            object.drawHouse(screen, self.player)

    def endLevel(self):
        self.player.wallToCheck.pop(-1)
        wall15 = Wall(None, width=430, height=100, xPOS=0, yPOS=736)
        wall16 = Wall(None, width=435, height=100, xPOS=565, yPOS=736)
        self.player.wallToCheck.append(wall15.wallRect)
        self.player.wallToCheck.append(wall16.wallRect)
        self.player.bulletList = []
        alpha = self.borderWallsImage.get_alpha()
        levelProgress["mainPatio"] = ["red", "haunted", "haunted"]
        self.player.attackMode = False
        if alpha != 0:
            self.borderWallsImage.set_alpha(alpha - 5)
        else:
            def interactableFunc1():
                self.interactable = None

            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 200,
                                             "You have saved the house from the ghosts!",
                                             [["OK", interactableFunc1]])
            self.enemyWave -= 1


class Level3:
    def __init__(self):
        self.previousPlayerProgress = playerProgress.copy()
        self.mainHouseProgress = levelProgress["mainHouse"]
        self.wallsList = []
        self.houseList = []
        self.enemysList = []
        self.decorationsList = []
        self.interactableObjectsList = []
        self.bg_image = pygame.image.load("pictures/Checkered-Floor400x320.png").convert_alpha()
        self.bg_image.set_alpha(128)
        self.walls()
        self.decorations()
        self.buildings()
        self.player = Player(30, 60, 500, 400, self.getBoundaries())
        self.borderWallsImage = pygame.image.load("pictures/insideLucaHouse.png").convert_alpha()
        self.enemyWave = None

        self.doorsInfo = [pygame.rect.Rect(430, 800, 135, 50), self.player.playerRect, Level1, 1]

        self.player.attackMode = False

        self.enemys()
        self.interactableObjects()

        self.interactable = None

    def walls(self):
        wall12 = Wall(None, width=10, height=800, xPOS=50 - 10, yPOS=0)
        wall13 = Wall(None, width=10, height=800, xPOS=945, yPOS=0)
        wall14 = Wall(None, width=1000, height=70, xPOS=0, yPOS=0)
        wall15 = Wall(None, width=430, height=100, xPOS=0, yPOS=736)
        wall16 = Wall(None, width=435, height=100, xPOS=565, yPOS=736)

        wall17 = Wall(None, width=100, height=330, xPOS=862, yPOS=355)
        wall18 = Wall(None, width=106, height=115, xPOS=506, yPOS=345)

        self.wallsList = [wall12, wall13, wall14, wall15, wall16, wall17, wall18]

        return self.wallsList

    def buildings(self):
        def interactableLevel1():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableLucaHouse():
            door([0, 0, Level2, 2, None])
            self.interactable = None

        def interactableDisappear():
            self.interactable = None

        def house1Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLucaHouse], ["No", interactableDisappear]])

        def house2Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def house3Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Luca's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        def house4Func():
            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,
                                             "Would you like to go inside Miranda's House",
                                             [["Yes", interactableLevel1], ["No", interactableDisappear]])

        # house1 = House(60, -50, 1, "blue", house1Func)
        # house2 = House(660, -50, 1, self.houseColorList[0], house2Func)
        # house3 = House(60, 550, 2, self.houseColorList[1], house3Func)
        # house4 = House(660, 550, 2, self.houseColorList[2], house4Func)
        # self.houseList = [house1, house2, house3, house4]

        return self.houseList

    def decorations(self):
        # coordinates = [[[6, 13], [19, 8]], [[6, 45], [19, 8]]]
        # plant0 = Decorations(10, 110, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant1 = Decorations(30, 60, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant2 = Decorations(20, 220, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant3 = Decorations(15, 140, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant4 = Decorations(27, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        #
        # plant5 = Decorations(38, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        #
        # plant6 = Decorations(130, 250, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant7 = Decorations(150, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant8 = Decorations(170, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant9 = Decorations(190, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant10 = Decorations(210, 270, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant11 = Decorations(230, 290, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant12 = Decorations(250, 300, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant13 = Decorations(270, 230, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        #
        # plant14 = Decorations(290, 120, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant15 = Decorations(310, 80, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant16 = Decorations(330, 260, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant17 = Decorations(350, 180, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant18 = Decorations(370, 240, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant19 = Decorations(240, 280, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)
        # plant20 = Decorations(280, 130, 20, 10, coordinates, "pictures/plant.png", imageRate=0.02)

        self.decorationsList = []

    def enemys(self):
        # enemy1 = Enemy("pictures/PlayerSpritesheet.png",
        #                30, 60, 700, 700,
        #                self.player.playerRect,
        #                self.player.bulletList, speed=4)

        self.enemysList = []
        return self.enemysList

    def getBoundaries(self):
        return self.wallsList + self.houseList

    def drawDecor(self, screen):
        for decor in self.decorationsList:
            decor.drawDecorations(screen)

    def drawWallsBehind(self, screen, playerY):
        for wall in self.wallsList:
            if playerY >= wall.wallRect.y:
                wall.drawWall(screen)

    def drawWallsFront(self, screen, playerY):
        for wall in self.wallsList:
            if playerY < wall.wallRect.y:
                wall.drawWall(screen)

    def drawHousesBehind(self, screen, playerY):
        for house in self.houseList:
            if playerY >= house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawHousesFront(self, screen, playerY):
        for house in self.houseList:
            if playerY < house.houseRect.y:
                house.drawHouse(screen, self.player)

    def drawInteractable(self, screen):
        if self.interactable != None:
            self.interactable.drawInteractable(screen)

    def drawMoveEnemy(self, screen):
        for enemy in self.enemysList:
            if enemy.alive == True:
                enemy.move()
                enemy.drawEnemy(screen)
            else:
                self.enemysList.remove(enemy)

    def drawBackGround(self, screen, widthS, heightS):
        pygame.draw.rect(screen, (242, 242, 242), pygame.rect.Rect(0, 0, widthS, heightS))
        screen.blit(pygame.transform.scale(self.bg_image, (widthS, heightS)), (0, 0))
        if self.borderWallsImage is not None:
            screen.blit(pygame.transform.scale(self.borderWallsImage, (widthS, heightS)), (0, 0))

    def interactableObjects(self):
        def interactableClothesBlue():
            playerProgress["playerOutfit"] = 0
            self.interactable = None

        def interactableClothesGreen():
            playerProgress["playerOutfit"] = 1
            self.interactable = None

        def interactableClothesPink():
            playerProgress["playerOutfit"] = 2
            self.interactable = None

        def interactableClothesRed():
            playerProgress["playerOutfit"] = 3
            self.interactable = None

        def interactableClothesYellow():
            playerProgress["playerOutfit"] = 4
            self.interactable = None

        def interactableDisappear():
            self.interactable = None

        def unlockClothesGreen():
            if playerProgress["playerCoins"] >= 100:
                playerProgress["playerCoins"] -= 100
                playerProgress["playerUnlockedOutfits"][1] = 1
                self.interactable = None
                object1Func()

        def unlockClothesPink():
            if playerProgress["playerCoins"] >= 100:
                playerProgress["playerCoins"] -= 100
                playerProgress["playerUnlockedOutfits"][2] = 1
                self.interactable = None
                object1Func()

        def unlockClothesRed():
            if playerProgress["playerCoins"] >= 100:
                playerProgress["playerCoins"] -= 100
                playerProgress["playerUnlockedOutfits"][3] = 1
                self.interactable = None
                object1Func()

        def unlockClothesYellow():
            if playerProgress["playerCoins"] >= 100:
                playerProgress["playerCoins"] -= 100
                playerProgress["playerUnlockedOutfits"][4] = 1
                self.interactable = None
                object1Func()

        def object1Func():
            buttonsList = [["Blue", interactableClothesBlue],
                           ["Green", interactableClothesGreen],
                           ["Pink", interactableClothesPink],
                           ["Red", interactableClothesRed],
                           ["Yellow", interactableClothesYellow],
                           ["No", interactableDisappear]]

            buttonsListLocked = [["Blue", interactableClothesBlue],
                                 ["100 Coins", unlockClothesGreen],
                                 ["100 Coins", unlockClothesPink],
                                 ["100 Coins", unlockClothesRed],
                                 ["100 Coins", unlockClothesYellow],
                                 ["No", interactableDisappear]]

            for index, outfit in enumerate(playerProgress["playerUnlockedOutfits"]):
                if outfit == 0:
                    buttonsList.pop(index)
                    buttonsList.insert(index, buttonsListLocked[index])

            self.interactable = Interactable(500, 300, (1000 / 2) - (500 / 2), 20,  # Blue. green, Pink, Red, Yellow
                                             "Would you like to change your clothes?", buttonsList)

        object1 = InteractableObject(870, 355, 100, 330, False, object1Func, sizeFromOrigin=20)
        self.interactableObjectsList = [object1]

        return self.interactableObjectsList

    def drawInteractableObjects(self, screen):
        for object in self.interactableObjectsList:
            object.drawHouse(screen, self.player)


game1 = Game(Level1)

game1.main()
