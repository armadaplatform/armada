from __future__ import print_function
from dockyard import alias


def add_arguments(parser):
    subparsers = parser.add_subparsers(help='Manage dockyard aliases', dest='dockyard_command')

    parser_set_help = 'Set dockyard alias'
    parser_set = subparsers.add_parser('set', help=parser_set_help, description=parser_set_help)
    parser_set.add_argument('name', help='Name of the dockyard alias')
    parser_set.add_argument('address', help='ip[:port] of the dockyard')
    parser_set.add_argument('--user', help='user')
    parser_set.add_argument('--password', help='password')
    parser_set.set_defaults(dockyard_func=command_dockyard_set)
    subparsers.add_parser(parser_set)

    parser_list_help = 'List dockyard aliases'
    parser_list = subparsers.add_parser('list', help=parser_list_help, description=parser_list_help)
    parser_list.set_defaults(dockyard_func=command_dockyard_list)
    subparsers.add_parser(parser_list)

    parser_remove_help = 'Delete dockyard alias'
    parser_remove = subparsers.add_parser('delete', help=parser_remove_help, description=parser_remove_help)
    parser_remove.add_argument('name', help='Name of the dockyard alias')
    parser_remove.set_defaults(dockyard_func=command_dockyard_remove)
    subparsers.add_parser(parser_remove)

    parser_default_help = 'Get or set default alias'
    parser_default = subparsers.add_parser('default', help=parser_default_help, description=parser_default_help)
    parser_default.add_argument('name', help='Name of the dockyard alias', nargs='?')
    parser_default.set_defaults(dockyard_func=command_dockyard_default)
    subparsers.add_parser(parser_default)


def command_dockyard(args):
    args.dockyard_func(args)


def command_dockyard_set(args):
    alias.set_alias(args.name, args.address, args.user, args.password)


def print_table(rows):
    widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    for row in rows:
        print('  '.join((str(val).ljust(width) for val, width in zip(row, widths))))


def command_dockyard_list(args):
    output_header = ['Default', 'Alias', 'Address', 'User', 'Password']
    output_rows = [output_header]
    alias_list = alias.get_list()
    for alias_dict in alias_list:
        default_string = '->'.rjust(len(output_header[0])) if alias_dict['is_default'] else ''
        row = [default_string, alias_dict['name'], alias_dict['address'], alias_dict.get('user', ''),
               _hide_password(alias_dict.get('password', ''))]
        output_rows.append(row)
    print_table(output_rows)


def _hide_password(password):
    return '****' if password else ''


def command_dockyard_remove(args):
    alias.remove_alias(args.name)


def command_dockyard_default(args):
    if args.name:
        alias.set_default(args.name)
    else:
        default_alias = alias.get_default()
        if default_alias:
            print('Default alias for dockyard is: {default_alias}'.format(**locals()))
        else:
            print('No default alias set')
