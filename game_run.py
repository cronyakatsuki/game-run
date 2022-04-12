#!/bin/env python3
import argparse
import sys
import os
import subprocess

VERSION="1.0"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='store_true', help='Print program version')
    parser.add_argument('game_path', type=str, metavar='GAME', action='store', nargs='?',
                        help="Command or path to the game you wanna run")
    parser.add_argument('-a', '--args', type=str, metavar='ARGUMENTS', action='store', 
                        help='Additional game arguments')
    parser.add_argument('-g', '--gamemode', action='store_true', help='Run game with gamemode')
    parser.add_argument('-m', '--mangohud', action='store_true', help='Run game with mangohud')
    parser.add_argument('-f', '--fps_limit', type=int, metavar='FPS', action='store',
                        help="Limit game fps (Must have libstrangle installed)")
    parser.add_argument('-w', '--wine', type=str, metavar='WINE', action='store',
                        help='Specify either WINE or PROTON version you wanna use(NEEDS FOR PREFIX TO BE SET)')
    parser.add_argument('-p', '--prefix', type=str, metavar='WINE_PREFIX', action='store',
                        help='Path to wine prefix')
    parser.add_argument('-s', '--sync', type=str, metavar='WINE_SYNC', action='store', 
                        help='Specify what sync method to use with WINE')
    parser.add_argument('--fsr', action='store_true', help='Enable fsr for any wine game')
    parser.add_argument('-d', '--dxvk', action='store_true', help='Enable specific dxvk settings')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    cmd=[]

    if args.version:
        print(f'Version: {VERSION}')
        sys.exit(0)

    if not args.game_path:
        print('Game path must be provided')
        sys.exit(1)

    if args.gamemode:
        cmd.append('gamemoderun')
    
    if args.gamemode:
        cmd.append('mangohud')

    if args.fps_limit:
        cmd.append('strangle')
        cmd.append(str(args.fps_limit))

    if args.wine and not args.prefix:
        print('Prefix must also be provided!')
        sys.exit(1)
    elif args.wine:
        os.environ['WINEPREFIX'] = args.prefix
        if args.wine == 'wine':
            cmd.append('wine')
        elif args.wine == 'proton':
            os.environ['STEAM_COMPAT_DATA_PATH'] = args.prefix
            os.environ['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = '/home/ivica/.steam/steam'
            cmd.append('/usr/share/steam/compatibilitytools.d/proton-ge-custom/proton')
            cmd.append('run')
        else:
            cmd.append(args.wine)

    if args.sync and not args.wine:
        print('Sync option needs for wine to be set!')
        sys.exit(1)
    elif args.sync:
        if args.sync == 'esync':
            os.environ['WINEESYNC'] = '1'
        if args.sync == 'fsync':
            os.environ['WINEFSYNC'] = '1'

    if args.fsr and not args.wine:
        print('Fsr option needs for wine to be set!')
        sys.exit(1)
    elif args.fsr:
        os.environ['WINE_FULLSCREEN_FSR'] = '1'
        os.environ['WINE_FULLSCREEN_FSR_STRENGHT'] = '2'

    if args.dxvk and not args.wine:
        print('Dxvk option needs for wine to be set!')
        sys.exit(1)
    elif args.dxvk:
        os.environ['DXVK_LOG_LEVEL'] = 'none'
        os.environ['DXVK_HUD'] = 'compiler'
        os.environ['DXVK_STATE_CACHE'] = '1'
        os.environ['DXVK_STATE_CACHE_PATH'] = args.prefix

    if args.game_path:
        cmd.append(args.game_path)

    if args.args:
        for arg in args.args.split(' '):
         cmd.append(arg)

    subprocess.Popen(cmd)
    sys.exit(0)

if __name__ == "__main__":
    main()
