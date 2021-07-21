import argparse

import argparse

def obtain_command_args():
    parser = argparse.ArgumentParser()
    #Serial arguments
    parser.add_argument('-c','--arduino_port', default="COM3", metavar='ARDUINO', help='arduino port')
    #Socket arguments
    parser.add_argument('--server_address', default="169.254.217.30", help='server socket. Replace it by the ip of the ethernet port')
    parser.add_argument('--server_port', default="5555", type=int, help='server port')
    parser.add_argument('--autonomy', action='store_true', default=False, help='If true, then the cognitive load will be used to control autonomy.'\
                                                                               ' Default(False), i.e., manual teleoperation')
    parser.add_argument('--debug', action='store_true', default=False, help='Skip serial and socket connections')
    args = parser.parse_args()

    return args
# parser.add_argument('-c','--arduino-port', action='store_const', const=True, default=False,
# 					metavar='FOO!')
# parser.add_argument('-f', '--foo2', metavar='YYY')
# parser.add_argument('--foo3', action='store_true', default=False, help='activate foo power')
# # parser.add_argument('--bee', const=True, default=False)
# parser.add_argument('bar', nargs=1)
# parser.add_argument('bar2', nargs=1)

