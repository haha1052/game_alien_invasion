import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((840, 800))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        # 创建存储游戏统计信息的实例，
        #  并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)  # 把一个Ship 类实例化为self.ship  括号里面的self 通过ai_game 传递了过去，是的Ship能够访问游戏资源
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.get_scores = self.settings.get_scores
        self.get_scores_limit = self.settings.get_scores_limt
        self.key_P_down = 0
        self._create_fleet()

        # 创建Play按钮
        self.play_button = Button(self, "play")

        # 设置背景色
        self.bg_color = (230, 230, 230)
        # 设置背景图片
        # bg =pygame.image.load("images/bg1.jpg").convert()
        # self.bg=pygame.transform.smoothscale(bg,self.screen.get_size())

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            if self.stats.game_active:
                # 每次循环时都重绘屏幕。
                self.ship.update()
                self._update_bullets()
                self.count_scores()
                # print(len(self.bullets))   # 检测子弹是否被删除掉
                self._update_aliens()

            self._update_screen()
            # 让最近绘制的屏幕可见

    def _check_events(self):
        # 响应键盘和鼠标事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # 在不定义函数，直接调用时，程序会卡住
                self._check_keydown_events(event)  # 需定义函数
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)  # 需定义函数
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            # 向右移动飞船
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            # 向左移动飞船
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            self.start_game()

    def _check_play_button(self, mouse_pos):
        """ 在玩家单击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)

        if button_clicked and not self.stats.game_active:
            self.start_game()

    def start_game(self):
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.settings.initialize_dynamic_settings()

        # 清空余下的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()

        # 创建一群新的外星人并让飞船居中
        self._create_fleet()
        self.ship.center_ship()

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)

    def _check_keyup_events(self, event):
        """响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """ 创建一颗子弹，并将其加入编组bullets中"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # 检查是否有子弹击中了外星人
        # 如果是就删除相应的子弹和外星人
        self._check_bullet_alien_collision()

    def _check_bullet_alien_collision(self):
        collision = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collision:
            for aliens in collision.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            # 删除现有子弹 并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.get_scores += 1

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def count_scores(self):
        if self.get_scores >= self.get_scores_limit:
            self.stats.game_active = False

    def _ship_hit(self):
        """ 响应飞船被外星人撞到"""

        # 将ships_left 减1
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            # 创建一群新的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()
            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """更新外星人群中所有外星人的位置"""
        # 检查是否有外星人位于边缘
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):  # 没有碰撞，返回None,if 代码不会执行，
            self._ship_hit()
        # 检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    def _create_alien(self, alien_number, row_number):
        """ 创建一个外星人并将其放在当前行 """
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将外星人下移并改变左右方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet(self):
        """ 创建外星人群"""
        # 创建一个外星人,并计算一行可容纳多少外星人
        # 外星人的间距为外星人宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        numbers_aliens_x = available_space_x // (2 * alien_width)

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(numbers_aliens_x):
                # 创建一个外星人并将其加入当前行
                self._create_alien(alien_number, row_number)

    # 创建第一行外星人   为什么当不使用方法绘制第一行外星人时，执行时只显示一个外星人
    def _check_aliens_bottom(self):
        """ 检查是否有外星人到达了屏幕底端。"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        # self.screen.blit(self.bg,(0,0))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # 显示得分
        self.sb.show_score()
        # 如果游戏处于非活动状态，就显示Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()
        # 让最近绘制的屏幕可见
        pygame.display.flip()  # 没有filp 函数，屏幕将跳一下就关闭
        # pygame.display.update()   # 两个函数相似


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
