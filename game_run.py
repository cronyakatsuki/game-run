#!/bin/env python3
import argparse
import sys
import os
import subprocess
import configparser
import pathlib

VERSION = "2"


def set_vsync(cmd, mode):
    if mode == 'opengl':
        cmd.append('-v')
        cmd.append('n')
    elif mode == 'vulkan':
        cmd.append('-v')
        cmd.append('3')
    return cmd


def set_fps(cmd, fps):
    cmd.append(fps)
    return cmd


def set_fps_dxvk(fps):
    os.environ['DXVK_FRAME_RATE'] = fps


def enable_mangohud(cmd, dlsym=False):
    cmd.append('mangohud')
    if dlsym:
        cmd.append('--dlsym')
    return cmd


def set_wine(cmd, prefix, wine):
    wine_version = pathlib.PurePath(wine).name
    os.environ['WINEPREFIX'] = prefix
    if wine_version == 'wine' or wine_version == 'wine64':
        cmd.append(wine)
    elif wine_version == 'proton':
        os.environ['STEAM_COMPAT_DATA_PATH'] = prefix
        os.environ['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser(
            '~/.steam/steam')
        if wine == 'proton':
            cmd.append(
                '/usr/share/steam/compatibilitytools.d/proton-ge-custom/proton')
        else:
            cmd.append(wine)
        cmd.append('run')
    if not os.path.exists(prefix):
        os.mkdir(prefix)

    return cmd


def set_wine_sync(sync):
    if sync == 'esync':
        os.environ['WINEESYNC'] = '1'
    if sync == 'fsync':
        os.environ['WINEFSYNC'] = '1'


def set_fsr():
    os.environ['WINE_FULLSCREEN_FSR'] = '1'
    os.environ['WINE_FULLSCREEN_FSR_STRENGHT'] = '2'


def set_dxvk_optimizations(prefix):
    os.environ['DXVK_LOG_LEVEL'] = 'none'
    os.environ['DXVK_HUD'] = 'compiler'
    os.environ['DXVK_STATE_CACHE'] = '1'
    os.environ['DXVK_STATE_CACHE_PATH'] = prefix


def set_nvidia_prime():
    os.environ['__NV_PRIME_RENDER_OFFLOAD'] = '1'
    os.environ['__VK_LAYER_NV_optimus'] = 'NVIDIA_only'
    os.environ['__GLX_VENDOR_LIBRARY_NAME'] = 'nvidia'


def set_java(cmd):
    cmd.append('java')
    cmd.append('-jar')
    return cmd


def set_steam(cmd, id):
    cmd.append('steam')
    cmd.append(f'steam://rungameid/{id}')
    return cmd


def set_lutris(cmd, id):
    cmd.append('lutris')
    cmd.append(f'lutris:rungameid/{id}')
    os.environ['LUTRIS_SKIP_INIT'] = '1'
    return cmd


def set_flatpak(cmd):
    cmd.append('flatpak')
    cmd.append('run')
    return cmd


def list_categories(config):
    categories = []
    for game in config.sections():
        if config.has_option(game, "category"):
            category = config.get(game, "category")
            if category not in categories:
                categories.append(category)

    for category in categories:
        print(category)


def list_by_category(list, config):
    if list == "categories":
        list_categories(config)
    else:
        for game in config.sections():
            if config.has_option(game, "category"):
                if config.get(game, "category") == list:
                    print(game)
    sys.exit(0)


def cmd_gen_config(config, cmd, game):
    if config.has_option(game, 'fps') and config.has_option(game, 'vsync'):
        cmd.append('strangle')
        cmd = set_fps(cmd, str(config.getint(game, 'fps')))
        cmd = set_vsync(cmd, config.get(game, 'vsync'))
    elif config.has_option(game, 'fps'):
        cmd.append('strangle')
        cmd = set_fps(cmd, str(config.getint(game, 'fps')))
    elif config.has_option(game, 'vsync'):
        cmd.append('strangle')
        cmd = set_vsync(cmd, config.get(game, 'vsync'))

    if config.has_option(game, 'fps_dxvk'):
        set_fps_dxvk(config.get(game, 'fps_dxvk'))

    if config.has_option(game, 'gamemode'):
        if config.getboolean(game, 'gamemode'):
            cmd.append('gamemoderun')

    if config.has_option(game, 'mangohud') and config.has_option(game, 'dlsym'):
        if config.getboolean(game, 'mangohud'):
            cmd = enable_mangohud(cmd, config.getboolean(game, 'dlsym'))
    elif config.has_option(game, 'mangohud'):
        if config.getboolean(game, 'mangohud'):
            cmd = enable_mangohud(cmd)

    if config.has_option(game, 'wine') and not config.has_option(game, 'prefix'):
        print('Prefix must also be provided in config!')
        sys.exit(1)
    elif config.has_option(game, 'wine'):
        cmd = set_wine(cmd, config.get(game, 'prefix'),
                       config.get(game, 'wine'))

    if config.has_option(game, 'sync') and not config.has_option(game, 'wine'):
        print('Sync option needs for wine to be set in config!')
        sys.exit(1)
    elif config.has_option(game, 'sync'):
        set_wine_sync(config.get(game, 'sync'))

    if config.has_option(game, 'fsr') and not config.has_option(game, 'wine'):
        print('Fsr option needs for wine to be set in config!')
        sys.exit(1)
    elif config.has_option(game, 'fsr'):
        if config.getboolean(game, 'fsr'):
            set_fsr()

    if config.has_option(game, 'dxvk') and not config.has_option(game, 'wine'):
        print('Dxvk option needs for wine to be set!')
        sys.exit(1)
    elif config.has_option(game, 'dxvk'):
        if config.getboolean(game, 'dxvk'):
            set_dxvk_optimizations(config.get(game, 'prefix'))

    if config.has_option(game, 'prime'):
        if config.getboolean(game, 'prime'):
            set_nvidia_prime()

    if config.has_option(game, 'java'):
        if config.getboolean(game, 'java'):
            cmd = set_java(cmd)

    if config.has_option(game, 'steam'):
        if config.getboolean(game, 'steam'):
            cmd = set_steam(cmd, config.get(game, 'path'))

    if config.has_option(game, 'lutris'):
        if config.getboolean(game, 'lutris'):
            cmd = set_lutris(cmd, config.get(game, 'path'))

    if config.has_option(game, 'flatpak'):
        if config.getboolean(game, 'flatpak'):
            cmd = set_flatpak(cmd)

    if config.has_option(game, 'path'):
        cmd.append(config.get(game, 'path'))

    if config.has_option(game, 'args'):
        for arg in config.get(game, 'args').split(' '):
            cmd.append(arg)

    if config.has_option(game, 'working_dir'):
        os.chdir(config.get(game, 'working_dir'))

    return cmd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='store_true',
                        help='Print program version')

    subparser = parser.add_subparsers(dest='command')

    list = subparser.add_parser(
        'list', help="List game category's or games from a category")
    list.add_argument('category', type=str, metavar='CATEGORY', action='store', nargs='?',
                      help="Category to print games from")

    launch = subparser.add_parser('launch', help="Launch specified game")
    launch.add_argument('game', type=str, metavar='GAME', action='store', nargs='?',
                        help="Game name from the config")

    config = configparser.ConfigParser()

    if os.path.isfile(os.path.expanduser("~/.config/game-run/config.ini")):
        configExists = True
        config.read(os.path.expanduser("~/.config/game-run/config.ini"))
    else:
        configExists = False

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    cmd = []

    if args.version:
        print(f'Version: {VERSION}')
        sys.exit(0)

    if not configExists:
        print("No config existing, add games first")
        sys.exit(1)

    if args.command == 'list':
        if args.category:
            list_by_category(args.category, config)
        else:
            list_categories(config)
        sys.exit(0)

    if args.command == 'launch':
        if args.game:
            cmd = cmd_gen_config(config, cmd, args.game)
        else:
            print('Game must be provided')
            sys.exit(1)

    subprocess.Popen(cmd)
    sys.exit(0)


if __name__ == "__main__":
    main()
