from army.api.command import get_army_parser

parser = get_army_parser()

parser.add_group(name="plugin1", help="Plugin1 Management Commands")