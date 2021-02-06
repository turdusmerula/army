from army.api.command import get_army_parser

parser = get_army_parser()

parser.add_group(name="plugin2", help="Plugin2 Management Commands")