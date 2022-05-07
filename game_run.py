#!/bin/env python3
import argparse
import sys
import os
import subprocess
import configparser

VERSION = "1.2"


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


def enable_mangohud(cmd):
    cmd.append('mangohud')
    cmd.append('--dlsym')
    return cmd


def set_wine(cmd, prefix, wine):
    os.environ['WINEPREFIX'] = prefix
    if wine == 'wine':
        cmd.append('wine')
    elif wine == 'proton':
        os.environ['STEAM_COMPAT_DATA_PATH'] = prefix
        os.environ['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser(
            '~/.steam/steam')
        cmd.append(
            '/usr/share/steam/compatibilitytools.d/proton-ge-custom/proton')
        cmd.append('run')
    else:
        cmd.append(wine)
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


def cmd_gen_args(args, cmd):
    if args.fps_limit and args.vsync:
        cmd.append('strangle')
        cmd = set_fps(cmd, str(args.fps_limit))
        cmd = set_vsync(cmd, args.vsync)
    elif args.fps_limit:
        cmd.append('strangle')
        cmd = set_fps(cmd, str(args.fps_limit))
    elif args.vsync:
        cmd.append('strangle')
        cmd = set_vsync(cmd, args.vsync)

    if args.gamemode:
        cmd.append('gamemoderun')

    if args.mangohud:
        cmd = enable_mangohud(cmd)

    if args.prefix and not args.wine:
        print('Wine needs to be provided with prefix!')
        sys.exit(1)

    if args.wine and not args.prefix:
        print('Prefix must also be provided!')
        sys.exit(1)
    elif args.wine:
        cmd = set_wine(cmd, args.prefix, args.wine)

    if args.sync and not args.wine:
        print('Sync option needs for wine to be set!')
        sys.exit(1)
    elif args.sync:
        set_wine_sync(args.sync)

    if args.fsr and not args.wine:
        print('Fsr option needs for wine to be set!')
        sys.exit(1)
    elif args.fsr:
        set_fsr()

    if args.dxvk and not args.wine:
        print('Dxvk option needs for wine to be set!')
        sys.exit(1)
    elif args.dxvk:
        set_dxvk_optimizations(args.prefix)

    if args.prime:
        set_nvidia_prime()

    if args.game:
        cmd.append(args.game)

    if args.args:
        for arg in args.args.split(' '):
            cmd.append(arg)

    if args.working_dir:
        os.chdir(args.working_dir)

    return cmd


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

    if config.has_option(game, 'gamemode'):
        if config.getboolean(game, 'gamemode'):
            cmd.append('gamemoderun')

    if config.has_option(game, 'mangohud'):
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
    parser.add_argument('game', type=str, metavar='GAME', action='store', nargs='?',
                        help="Command or path to the game you wanna run")
    parser.add_argument('-a', '--args', type=str, metavar='ARGUMENTS', action='store',
                        help='Additional game arguments')
    parser.add_argument('-g', '--gamemode', action='store_true',
                        help='Run game with gamemode')
    parser.add_argument('-m', '--mangohud', action='store_true',
                        help='Run game with mangohud')
    parser.add_argument('-f', '--fps_limit', type=int, metavar='FPS', action='store',
                        help="Limit game fps (Must have libstrangle installed)")
    parser.add_argument('--vsync', type=str, metavar='VSYNC', action='store',
                        help="Set vsync on for either opengl or vulkan (Must have libstrangle installed)")
    parser.add_argument('-w', '--wine', type=str, metavar='WINE', action='store',
                        help='Specify either WINE or PROTON version you wanna use(NEEDS FOR PREFIX TO BE SET)')
    parser.add_argument('-p', '--prefix', type=str, metavar='WINE_PREFIX', action='store',
                        help='Path to wine prefix')
    parser.add_argument('-s', '--sync', type=str, metavar='WINE_SYNC', action='store',
                        help='Specify what sync method to use with WINE')
    parser.add_argument('--fsr', action='store_true',
                        help='Enable fsr for any wine game')
    parser.add_argument('-d', '--dxvk', action='store_true',
                        help='Enable specific dxvk settings')
    parser.add_argument('--prime', action='store_true',
                        help='Use dedicated gpu on an optimus system')
    parser.add_argument('--working_dir', type=str, metavar='WORKING_DIRECTORY', action='store',
                        help='Set the working directory for games that need it')

    config = configparser.ConfigParser()

    if os.path.exists(os.path.expanduser("~/.config/game-run")) and os.path.isfile(os.path.expanduser("~/.config/game-run/config.ini")):
        configExists = True
        config.read(os.path.expanduser("~/.config/game-run/config.ini"))
    else:
        configExists = False

    if len(sys.argv) == 1 and not configExists:
        parser.print_help()
        sys.exit(1)
    elif len(sys.argv) == 1 and len(config.sections()) == 0:
        parser.print_help()
        sys.exit(1)
    elif len(sys.argv) == 1 and not len(config.sections()) == 0:
        for game in config.sections():
            print(game)
        sys.exit(0)

    args = parser.parse_args()

    cmd = []

    if args.version:
        print(f'Version: {VERSION}')
        sys.exit(0)

    if not args.game:
        print('Game must be provided')
        sys.exit(1)

    if len(sys.argv) == 2 and configExists and config.has_section(args.game):
        cmd = cmd_gen_config(config, cmd, args.game)
    else:
        cmd = cmd_gen_args(args, cmd)

    subprocess.Popen(cmd)
    sys.exit(0)


if __name__ == "__main__":
    main()
