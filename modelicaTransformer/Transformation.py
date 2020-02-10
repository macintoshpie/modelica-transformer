from collections import namedtuple

from modelicaTransformer.Selector import ComponentArgSelector
from modelicaTransformer.Edit import Edit

# Transformation is an abstraction of a collection of nodes and changes to those nodes
# selector indicates which nodes to apply the change to
# edit indicates the change to apply
Transformation = namedtuple('Transformation', ['selector', 'edit'])

def ReplaceComponentArgumentValue(component_identifier, argument_name, new_value):
  """ReplaceComponentArgumentValue creates a transformation which changes a component's
  initialization value for an argument

  :param component_identifier: string, identifier of the component in the class
  :param argument_name: string, name of argument to modify
  :param new_value: string, new argument value
  :return: Transformation
  """
  selector = ComponentArgSelector(component_identifier, argument_name)
  edit = Edit.makeReplace(new_value)
  return Transformation(selector, edit)