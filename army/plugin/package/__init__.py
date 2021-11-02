import army.api.command

package_group = army.api.command.get_army_parser().add_group(name="package", help="Packaging Management Commands")

import army.plugin.package.package
import army.plugin.package.publish
