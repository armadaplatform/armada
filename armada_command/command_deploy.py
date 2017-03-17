from armada_command import command_run
from armada_command.command_restart import command_restart


def add_arguments(parser):
    parser.add_argument('-n', '--num-instances', help='Number of instances that should be deployed.', type=int,
                        default=1)
    command_run.add_arguments(parser)


def command_deploy(args):
    args.all = True
    args.microservice_handle = args.microservice_name
    command_restart(args)
