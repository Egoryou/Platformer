import pygame
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
LEVEL_WIDTH = 4000
LEVEL_HEIGHT = 800


class Player(pygame.sprite.Sprite):
    """Представляет управляемого игроком персонажа

    :ivar image: Графическое представление персонажа
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    :ivar vel_x: Скорость по оси X
    :type vel_x: int
    :ivar vel_y: Скорость по оси Y
    :type vel_y: int
    :ivar speed: Базовая скорость движения
    :type speed: int
    :ivar jump_power: Сила прыжка
    :type jump_power: int
    :ivar gravity: Сила гравитации
    :type gravity: float
    :ivar on_ground: Флаг нахождения на поверхности
    :type on_ground: bool
    :ivar lives: Количество жизней (начальное: 3)
    :type lives: int
    :ivar score: Набранные очки
    :type score: int
    :ivar speed_boost: Бонус скорости
    :type speed_boost: int
    :ivar speed_boost_time: Время окончания действия бонуса скорости
    :type speed_boost_time: int
    :ivar immune: Флаг иммунитета к урону
    :type immune: bool
    :ivar immune_time: Время окончания иммунитета
    :type immune_time: int
    """

    def __init__(self, x, y):
        """
        Конструктор класса Player

        :param x: Начальная координата X
        :type x: int
        :param y: Начальная координата Y
        :type y: int
        """
        super().__init__()
        try:
            self.original_image = pygame.image.load('pictures/hero.png').convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (50, 70))
        except FileNotFoundError:
            self.image = pygame.Surface((50, 70))
            self.image.fill((50, 100, 255))
            self.original_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6
        self.jump_power = 15
        self.gravity = 0.8
        self.on_ground = False
        self.lives = 3
        self.score = 0
        self.speed_boost = 0
        self.speed_boost_time = 0
        self.immune = False
        self.immune_time = 0

    def update(self, platforms, spikes, turrets, collectibles, screen_width, screen_height, camera_x, camera_y):
        """
        Обновляет состояние игрока каждый кадр

        :param platforms: Группа платформ для проверки коллизий
        :type platforms: pygame.sprite.Group
        :param spikes: Группа шипов
        :type spikes: pygame.sprite.Group
        :param turrets: Группа турелей
        :type turrets: pygame.sprite.Group
        :param collectibles: Группа собираемых предметов
        :type collectibles: pygame.sprite.Group
        :param screen_width: Ширина экрана
        :type screen_width: int
        :param screen_height: Высота экрана
        :type screen_height: int
        :param camera_x: Позиция камеры по X
        :type camera_x: int
        :param camera_y: Позиция камеры по Y
        :type camera_y: int
        """
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        speed = self.speed + self.speed_boost
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = speed

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH
        if self.rect.top > LEVEL_HEIGHT + 100:
            self.lives -= 1
            self.rect.x = 100
            self.rect.y = 100
            self.vel_y = 0

        current_time = pygame.time.get_ticks()
        if current_time > self.speed_boost_time:
            self.speed_boost = 0

        if current_time > self.immune_time:
            self.immune = False

        if not self.immune:
            for spike in spikes:
                if self.rect.colliderect(spike.rect):
                    self.lives -= 1
                    self.immune = True
                    self.immune_time = current_time + 1000
                    self.vel_y = -10
                    break

        if not self.immune:
            for turret in turrets:
                for bullet in turret.bullets:
                    if self.rect.colliderect(bullet.rect):
                        self.lives -= 1
                        self.immune = True
                        self.immune_time = current_time + 1000
                        turret.bullets.remove(bullet)

        for collectible in collectibles:
            if self.rect.colliderect(collectible.rect):
                collectible.apply_effect(self)
                collectibles.remove(collectible)
                self.score += 10

        if self.immune:
            self.image = self.original_image.copy()
            blue_filter = pygame.Surface(self.image.get_size())
            blue_filter.fill((100, 200, 255))
            self.image.blit(blue_filter, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.image = pygame.transform.scale(self.image, (50, 70))
        else:

            self.image = pygame.transform.scale(self.original_image, (50, 70))


class Platform(pygame.sprite.Sprite):
    """Представляет статичную поверхность для передвижения игрока

    :ivar image: Графическое представление платформы
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    """

    def __init__(self, x, y, width, height):
        """
        Конструктор класса Platform

        :param x: Координата X левого верхнего угла
        :type x: int
        :param y: Координата Y левого верхнего угла
        :type y: int
        :param width: Ширина платформы
        :type width: int
        :param height: Высота платформы
        :type height: int
        """
        super().__init__()
        try:
            self.image = pygame.image.load('pictures/platform.png').convert()
            self.image = pygame.transform.scale(self.image, (width, height))
        except FileNotFoundError:
            self.image = pygame.Surface((width, height))
            self.image.fill((139, 69, 19))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class VerticalPlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        try:
            self.image = pygame.image.load('pictures/vertical_platform.png').convert()
            self.image = pygame.transform.scale(self.image, (width, height))
        except FileNotFoundError:
            self.image = pygame.Surface((width, height))
            self.image.fill((139, 69, 19))


class Spike(pygame.sprite.Sprite):
    """Представляет опасное препятствие, наносящее урон при касании

    :ivar image: Графическое представление шипа
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    """

    def __init__(self, x, y, width=30, height=30):
        """
        Конструктор класса Spike

        :param x: Координата X левого верхнего угла
        :type x: int
        :param y: Координата Y левого верхнего угла
        :type y: int
        :param width: Ширина шипа, по умолчанию 30
        :type width: int
        :param height: Высота шипа, по умолчанию 30
        :type height: int
        """
        super().__init__()
        try:
            self.original_image = pygame.image.load('pictures/spike.png').convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (width, height))
        except FileNotFoundError:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 50, 50), [(width // 2, 0), (0, height), (width, height)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Turret(pygame.sprite.Sprite):
    """Представляет стреляющую турель с заданным направлением

    :ivar image: Графическое представление турели
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    :ivar direction: Направление стрельбы
    :type direction: str
    :ivar bullets: Список активных пуль
    :type bullets: list
    :ivar last_shot: Время последнего выстрела
    :type last_shot: int
    :ivar shoot_delay: Задержка между выстрелами в миллисекундах
    :type shoot_delay: int
    """

    def __init__(self, x, y, direction="right"):
        """
        Конструктор класса Turret

        :param x: Координата X левого верхнего угла
        :type x: int
        :param y: Координата Y левого верхнего угла
        :type y: int
        :param direction: Направление стрельбы ("left" или "right"), по умолчанию "right"
        :type direction: str
        """
        super().__init__()
        try:
            self.image = pygame.transform.scale(pygame.image.load('pictures/turret.png').convert_alpha(), (70, 60))
            self.base_image = self.image.copy()
            if direction == "right":
                self.base_image = pygame.transform.flip(self.base_image, True, False)
        except FileNotFoundError:
            self.base_image = pygame.Surface((70, 60), pygame.SRCALPHA)
            self.base_image.fill((50, 255, 50))
            self.image = self.base_image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.direction = direction
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 2000

    def update(self, player, platforms=None):
        """
        Обновляет состояние турели каждый кадр

        :param player: Объект игрока
        :type player: Player
        :param platforms: Группа платформ для проверки коллизий пуль
        :type platforms: list
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = current_time

        for bullet in self.bullets[:]:
            collided = bullet.update(platforms)
            if collided:
                self.bullets.remove(bullet)

    def shoot(self):
        """
        Производит выстрел из турели
        """
        if self.direction == "right":
            bullet = Bullet(self.rect.right, self.rect.centery, 5, 0)
        else:
            bullet = Bullet(self.rect.left, self.rect.centery, -5, 0)
        self.bullets.append(bullet)


class Bullet(pygame.sprite.Sprite):
    """Представляет снаряд, выпущенный турелью

    :ivar image: Графическое представление пули
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    :ivar vel_x: Скорость по оси X
    :type vel_x: int
    :ivar vel_y: Скорость по оси Y
    :type vel_y: int
    """

    def __init__(self, x, y, vel_x, vel_y):
        """
        Конструктор класса Bullet

        :param x: Координата X центра пули
        :type x: int
        :param y: Координата Y центра пули
        :type y: int
        :param vel_x: Скорость по оси X
        :type vel_x: int
        :param vel_y: Скорость по оси Y
        :type vel_y: int
        """
        super().__init__()
        try:
            self.image = pygame.image.load('pictures/bullet.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (15, 15))
            if vel_x > 0:
                self.image = pygame.transform.flip(self.image, True, False)
        except FileNotFoundError:
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = vel_x
        self.vel_y = vel_y

    def update(self, platforms=None):
        """
        Обновляет положение пули с проверкой коллизий

        :param platforms: Группа платформ для проверки коллизий (опционально)
        :return: True если пуля столкнулась с платформой, иначе False
        """
        old_rect = self.rect.copy()

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.rect.x = old_rect.x
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    else:
                        self.rect.left = platform.rect.right
                    return True

        if self.rect.right < -50 or self.rect.left > LEVEL_WIDTH + 50:
            return True

        return False


class Collectible(pygame.sprite.Sprite):
    """Представляет бонус, который можно собрать для получения различных эффектов
    :ivar image: Графическое представление предмета
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    :ivar type: Тип предмета ("life", "speed" или "immune")
    :type type: str
    """

    def __init__(self, x, y, type="life"):
        """
        Конструктор класса Collectible

        :param x: Координата X левого верхнего угла
        :type x: int
        :param y: Координата Y левого верхнего угла
        :type y: int
        :param type: Тип предмета ("life", "speed" или "immune"), по умолчанию "life"
        :type type: str
        """
        super().__init__()
        self.type = type

        image_files = {
            "life": "pictures/heart.png",
            "speed": "pictures/speed.png",
            "immune": "pictures/immune.png"
        }

        try:
            filename = image_files[type]
            self.image = pygame.image.load(filename).convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))

        except FileNotFoundError:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            if type == "life":
                self.image.fill((255, 50, 50))
            elif type == "speed":
                self.image.fill((255, 255, 0))
            elif type == "immune":
                self.image.fill((120, 120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def apply_effect(self, player):
        """
        Применяет эффект предмета к игроку

        :param player: Объект игрока, к которому применяется эффект
        :type player: Player
        """
        if self.type == "life":
            player.lives += 1
        elif self.type == "speed":
            player.speed_boost = 3
            player.speed_boost_time = pygame.time.get_ticks() + 5000
        elif self.type == "immune":
            player.immune = True
            player.immune_time = pygame.time.get_ticks() + 3000


class Checkpoint(pygame.sprite.Sprite):
    """Представляет цель уровня, достижение которой означает победу
    :ivar image: Графическое представление флага
    :type image: pygame.Surface
    :ivar rect: Прямоугольник для коллизий и позиционирования
    :type rect: pygame.Rect
    :ivar active: Флаг активности точки сохранения
    :type active: bool
    """

    def __init__(self, x, y):
        """
        Конструктор класса Checkpoint

        :param x: Координата X левого верхнего угла
        :type x: int
        :param y: Координата Y левого верхнего угла
        :type y: int
        """
        super().__init__()
        try:
            self.image = pygame.image.load('pictures/finish.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 80))
        except FileNotFoundError:
            self.image = pygame.Surface((40, 60))
            self.image.fill((50, 255, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.active = True

    def update(self, player):
        """
        Проверяет, достиг ли игрок точки сохранения

        :param player: Объект игрока
        :type player: Player
        :returns: True если игрок достиг точки сохранения, иначе False
        :rtype: bool
        """
        if self.active and player.rect.colliderect(self.rect):
            self.active = False
            return True
        return False


def create_level():
    """
    Создает и настраивает игровой уровень

    :returns: Кортеж объектов уровня (platforms, spikes, turrets, collectibles, checkpoint)
    :rtype: tuple
    """
    platforms = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    turrets = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    platforms.add(Platform(0, LEVEL_HEIGHT - 40, LEVEL_WIDTH, 40))
    horizontal_platforms = [
        (200, 700, 200, 30),
        (600, 650, 180, 25),
        (1000, 600, 160, 20),
        (1400, 650, 200, 30),
        (1800, 600, 180, 25),
        (2200, 550, 150, 25),
        (2600, 400, 200, 30),
        (3000, 350, 180, 25),
        (3400, 400, 160, 20),
        (3800, 350, 200, 30),
        (3500, 300, 180, 25),
        (3900, 250, 150, 25),
    ]

    for x, y, width, height in horizontal_platforms:
        platforms.add(Platform(x, y, width, height))

    vertical_platforms = [
        (500, 600, 30, 150),
        (1500, 550, 25, 120),
        (2500, 450, 35, 180),
        (3500, 370, 30, 150),
        (800, 620, 20, 100),
        (1700, 590, 25, 90),
        (2800, 370, 30, 130),
    ]

    for x, y, width, height in vertical_platforms:
        platforms.add(VerticalPlatform(x, y, width, height))

    spikes_data = [
        (425, LEVEL_HEIGHT - 90, 50, 50),
        (1200, LEVEL_HEIGHT - 70, 30, 30),
        (2000, LEVEL_HEIGHT - 70, 30, 30),
        (2200, 520, 30, 30),
        (3150, 300, 50, 50),
        (3900, 200, 50, 50),
    ]

    for x, y, width, height in spikes_data:
        spikes.add(Spike(x, y, width, height))

    turrets_data = [
        (980, 550, "left"),
        (1900, 550, "left"),
        (3500, 250, "left"),
    ]

    for x, y, direction in turrets_data:
        turrets.add(Turret(x, y, direction))

    items_data = [
        (700, 600, "speed"),
        (1300, 600, "immune"),
        (1600, 550, "life"),
        (2100, 500, "speed"),
        (2650, 350, "life"),
        (3100, 300, "speed"),
        (3450, 350, "immune"),
        (3600, 250, "life"),
        (3950, 200, "speed"),
        (2750, 320, "immune"),
    ]

    for x, y, item_type in items_data:
        collectibles.add(Collectible(x, y, item_type))

    checkpoint = Checkpoint(3950, 200)

    return platforms, spikes, turrets, collectibles, checkpoint


def main():
    """
    Главная функция игры
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer")
    clock = pygame.time.Clock()
    try:
        bg_tile = pygame.image.load('pictures/background.png').convert()
        tile_width, tile_height = bg_tile.get_size()
        bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for x in range(0, SCREEN_WIDTH, tile_width):
            for y in range(0, SCREEN_HEIGHT, tile_height):
                bg_image.blit(bg_tile, (x, y))

    except FileNotFoundError:
        bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_image.fill((100, 100, 100))
    platforms, spikes, turrets, collectibles, checkpoint = create_level()
    player = Player(100, 100)
    camera_x = 0
    camera_y = 0
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    game_over = False
    game_won = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if (game_over or game_won) and event.key == pygame.K_r:
                    platforms, spikes, turrets, collectibles, checkpoint = create_level()
                    player = Player(100, 100)
                    game_over = False
                    game_won = False
                    camera_x = 0
                    camera_y = 0

        if not game_over and not game_won:
            player.update(platforms, spikes, turrets, collectibles, SCREEN_WIDTH, SCREEN_HEIGHT, camera_x, camera_y)
            for turret in turrets:
                turret.update(player, platforms)
            if checkpoint.update(player):
                game_won = True
            if player.lives <= 0:
                game_over = True
            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2
            if camera_x < 0:
                camera_x = 0
            if camera_x > LEVEL_WIDTH - SCREEN_WIDTH:
                camera_x = LEVEL_WIDTH - SCREEN_WIDTH
            if camera_y < 0:
                camera_y = 0
            if camera_y > LEVEL_HEIGHT - SCREEN_HEIGHT:
                camera_y = LEVEL_HEIGHT - SCREEN_HEIGHT
        screen.blit(bg_image, (0, 0))
        for platform in platforms:
            screen.blit(platform.image, (platform.rect.x - camera_x, platform.rect.y - camera_y))
        for spike in spikes:
            screen.blit(spike.image, (spike.rect.x - camera_x, spike.rect.y - camera_y))
        for turret in turrets:
            screen.blit(turret.image, (turret.rect.x - camera_x, turret.rect.y - camera_y))
            for bullet in turret.bullets:
                screen.blit(bullet.image, (bullet.rect.x - camera_x, bullet.rect.y - camera_y))
        for collectible in collectibles:
            screen.blit(collectible.image, (collectible.rect.x - camera_x, collectible.rect.y - camera_y))
        screen.blit(checkpoint.image, (checkpoint.rect.x - camera_x, checkpoint.rect.y - camera_y))
        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
        lives_text = font.render(f"Жизни: {player.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (10, 10))
        score_text = font.render(f"Счёт: {player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 50))
        controls_text = small_font.render("Управление: <- ->/A D - движение, W/Пробел - прыжок", True, (255, 255, 255))
        screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 10, 10))
        if game_won:
            win_text = font.render("УРОВЕНЬ ПРОЙДЕН! Нажмите R для перезапуска", True, (50, 255, 50))
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        if game_over:
            lose_text = font.render("ВЫ ПРОИГРАЛИ! Нажмите R для перезапуска", True, (255, 50, 50))
            screen.blit(lose_text, (SCREEN_WIDTH // 2 - lose_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
