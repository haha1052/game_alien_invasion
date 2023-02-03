import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """ 管理飞船的类"""
    # 传递的ai_game 可以看出来是一个对象，并且估计有一个类可用来实例化
    def __init__(self,ai_game):
        """初始化飞船并设置其初始位置"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()    # get_rect() 访问屏幕的属性rect:

        # 加载 飞船图像 并获取其外接矩形
        self.image = pygame.image.load("images/ship.bmp")
        # 测试是否可以旋转 ,验证成功
        # self.image = pygame.transform.rotate(self.image,-90)

        self.rect = self.image.get_rect()     # get_rect() 函数是什么函数呢？

        # 对每艘新飞船，都将其放在屏幕的底部的中央。
        self.rect.midbottom = self.screen_rect.midbottom   #可以用(x,y) 替换，原点（0，0）为屏幕左上角
        # self.rect.midbottom = (500,650)       # 验证可以
        # 在飞船的属性x中存储小数值
        self.x =float(self.rect.x)
        #移动标志
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """ 根据移动标志调整飞船的位置"""
        # 更新飞船而不是rect对象的x值
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x +=  self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:  #0就是最左边的位置
            self.x -= self.settings.ship_speed
        # 根据self.x更新rect对象
        self.rect.x = self.x

    def blitme(self):
        """ 在指定位置绘制飞船"""
        # blict() 方法可以用来绘制位图

        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """ 让飞船在屏幕底端居中 """
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
