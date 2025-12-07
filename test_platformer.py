import pygame
from unittest.mock import Mock, patch
from platformer import (
    Player, Platform, Spike, Turret, Bullet,
    Collectible, Checkpoint, create_level,
)


def test_player_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        player = Player(100, 200)
        assert player.rect.x == 100
        assert player.rect.y == 200
        assert player.speed == 6
        assert player.lives == 3
        assert player.score == 0
        assert player.immune == False


def test_player_move_left():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        player = Player(100, 100)
        mock_keys = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player.update([], [], [], [], 1000, 600, 0, 0)
            assert player.vel_x == -6
            assert player.vel_y > 0


def test_player_move_right():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        player = Player(100, 100)
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: True,
            pygame.K_UP: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }

        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player.update([], [], [], [], 1000, 600, 0, 0)
            assert player.vel_x == 6
            assert player.vel_y > 0


def test_player_jump():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        player = Player(100, 100)
        player.on_ground = True
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: True,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }

        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player.update([], [], [], [], 1000, 600, 0, 0)
            assert player.vel_y == -14.2
            assert player.on_ground == False


def test_player_jump_not_on_ground():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        player = Player(100, 100)
        player.on_ground = False

        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: True,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }

        original_vel_y = player.vel_y

        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player.update([], [], [], [], 1000, 600, 0, 0)
            assert player.vel_y != -15
            assert player.vel_y == original_vel_y + player.gravity


def test_platform_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        platform = Platform(200, 300, 150, 20)

        assert platform.rect.x == 200
        assert platform.rect.y == 300
        assert platform.rect.width == 150
        assert platform.rect.height == 20


def test_spike_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        spike = Spike(300, 400)

        assert spike.rect.x == 300
        assert spike.rect.y == 400


def test_spike_custom_size():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        spike = Spike(300, 400, width=40, height=40)

        assert spike.rect.width == 40
        assert spike.rect.height == 40


def test_turret_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        turret = Turret(500, 200, "right")

        assert turret.rect.x == 500
        assert turret.rect.y == 200
        assert turret.direction == "right"
        assert len(turret.bullets) == 0


def test_turret_shoot_right():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        turret = Turret(500, 200, "right")

        turret.shoot()

        assert len(turret.bullets) == 1
        bullet = turret.bullets[0]
        assert bullet.vel_x == 5
        assert bullet.vel_y == 0


def test_turret_shoot_left():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        turret = Turret(500, 200, "left")
        turret.shoot()
        assert len(turret.bullets) == 1
        bullet = turret.bullets[0]
        assert bullet.vel_x == -5
        assert bullet.vel_y == 0


def test_bullet_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        bullet = Bullet(600, 300, 5, 0)
        assert bullet.rect.center == (600, 300)
        assert bullet.vel_x == 5
        assert bullet.vel_y == 0


def test_bullet_update():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        bullet = Bullet(600, 300, 5, 2)
        initial_x = bullet.rect.x
        initial_y = bullet.rect.y
        bullet.update()
        assert bullet.rect.x == initial_x + 5
        assert bullet.rect.y == initial_y + 2


def test_collectible_initialization_life():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "life")
        assert collectible.rect.x == 700
        assert collectible.rect.y == 400
        assert collectible.type == "life"


def test_collectible_initialization_speed():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "speed")

        assert collectible.rect.x == 700
        assert collectible.rect.y == 400
        assert collectible.type == "speed"


def test_collectible_initialization_immune():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "immune")
        assert collectible.rect.x == 700
        assert collectible.rect.y == 400
        assert collectible.type == "immune"


def test_collectible_apply_effect_life():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "life")
        player = Mock(lives=3)
        collectible.apply_effect(player)
        assert player.lives == 4


def test_collectible_apply_effect_speed():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "speed")
        player = Mock(speed_boost=0, speed_boost_time=0)
        with patch('pygame.time.get_ticks', return_value=1000):
            collectible.apply_effect(player)
            assert player.speed_boost == 3
            assert player.speed_boost_time == 6000


def test_collectible_apply_effect_immune():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        collectible = Collectible(700, 400, "immune")
        player = Mock(immune=False, immune_time=0)
        with patch('pygame.time.get_ticks', return_value=1000):
            collectible.apply_effect(player)
            assert player.immune == True
            assert player.immune_time == 4000


def test_checkpoint_initialization():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        checkpoint = Checkpoint(1800, 350)
        assert checkpoint.rect.x == 1800
        assert checkpoint.rect.y == 350
        assert checkpoint.active == True


def test_checkpoint_update_with_collision():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        checkpoint = Checkpoint(1800, 350)
        player = Mock()
        player.rect.colliderect = Mock(return_value=True)
        result = checkpoint.update(player)
        assert result == True
        assert checkpoint.active == False


def test_checkpoint_update_without_collision():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        checkpoint = Checkpoint(1800, 350)
        player = Mock()
        player.rect.colliderect = Mock(return_value=False)
        result = checkpoint.update(player)
        assert result == False
        assert checkpoint.active == True


def test_create_level():
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        platforms, spikes, turrets, collectibles, checkpoint = create_level()
        assert len(platforms) > 0
        assert len(spikes) > 0
        assert len(turrets) > 0
        assert len(collectibles) > 0
        assert checkpoint is not None
        assert len(platforms) == 20
        assert len(spikes) == 6
        assert len(turrets) == 3
        assert len(collectibles) == 10
