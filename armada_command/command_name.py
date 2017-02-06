import armada_api


def add_arguments(parser):
    parser.add_argument('name', help='New name for the ship', nargs='?', default='')


def command_name(args):
    if args.name:
        result = armada_api.post('name', {'name': args.name})
        armada_api.print_result_from_armada_api(result)
    else:
        result = armada_api.get('name')
        print(result)
