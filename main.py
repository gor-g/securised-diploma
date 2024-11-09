import argparse
from runner import Runner

parser = argparse.ArgumentParser(description="A tool to build securized diplommas using steganography")

subparsers = parser.add_subparsers(dest='command', help='commands')

parser_insert = subparsers.add_parser('insert', help='Insert a steganographic message into an image')
parser_insert.add_argument('image', type=str, help='path to the image to hide the message in')
parser_insert.add_argument('message', type=str, help='plain text message')
parser_insert.add_argument('output', type=str, help='path to the output image')

parser_extract = subparsers.add_parser('extract', help='Extract a steganographic message from an image')
parser_extract.add_argument('image', type=str, help='path to the image containing the stenographic message')

parser_text = subparsers.add_parser('text', help='Insert text into a picture')
parser_text.add_argument('template', type=str, help='path to the dimploma template image')
parser_text.add_argument('message', type=str, help='plain text message')
parser_text.add_argument('output', type=str, help='path to the output image')

parser_create = subparsers.add_parser('create', help='Create a diploma')
# parser_create.add_argument('template', type=str, help='path to the dimploma template image')
parser_create.add_argument('student', type=str, help='plain text ')
parser_create.add_argument('date_birth', type=str, help="student's date of birth")
parser_create.add_argument('year', type=int, help="the year of obtention of the diploma")
parser_create.add_argument('average', type=float, help='average score')
parser_create.add_argument('merit', type=str, help='merit')
# parser_create.add_argument('output', type=str, help='path to the output image')

parser_verify = subparsers.add_parser('verify', help='Verify a steganographic diploma')
parser_verify.add_argument('student', type=str, help='firstname LASTNAME')
# parser_verify.add_argument('diploma', type=str, help='path to the image')
# parser_verify.add_argument('message', type=str, help='plain text message to verify')


args = parser.parse_args()

Runner().run(args.__dict__)