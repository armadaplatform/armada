from armada_command import armada_api


def command_shutdown(args):
    result = armada_api.post('shutdown', {'keep-joined': args.keep_joined})
    armada_api.print_result_from_armada_api(result)


def add_arguments(parser):
    parser.add_argument('--keep-joined', action='store_true', default=False,
                        help="Keep currently joined ships. Otherwise it clears ships in "
                             "/opt/armada/runtime_settings.json")
