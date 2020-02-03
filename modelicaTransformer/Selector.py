from antlr4.xpath import XPath


def select(root, parser, rule, child=None, child_value=None):
  """selects the rule that has a child with child_value
  e.g. select a component whose identifier is thermalZoneTwoElements

  :param root: object, tree to search
  :param parser: object, parser that generated the tree
  :param rule: string, name of node to search for
  :param child: string, name of direct descendant to inspect text of
  :param child_value: string, value to filter nodes
  """
  matches = XPath.XPath.findAll(root, f'//{rule}', parser)
  if len(matches) == 0:
    return []
  
  # check if we need to do filtering
  if child == None:
    return matches

  def nothing():
    pass

  results = []
  for match in matches:
    # get the child's text
    val = getattr(match, child, nothing)().getText()
    if val == child_value:
      results.append(match)
  
  return results


def parseSelectors(path):
  raise Exception("not implemented")
  

def selectPath(root, parser, path):
  """selects nodes based on a series of node selectors

  :param root: object, tree root to search
  :param parser: object, parser that made the tree
  :param path: list, sparse path to a node
  """
  # TODO: refactor path to be a string which we parse into selectors
  # e.g.: "declaration[IDENT=thermalZoneTwoElements].element_modification[name=VAir].expression"
  # selectors = parseSelectors(path)
  selectors = path

  selected_nodes = [root]
  # for each selector, apply it to our selected nodes
  for selector in selectors:
    # early exit if search ends
    if not selected_nodes:
      return []
  
    new_roots = []
    for node in selected_nodes:
      new_roots += select(
                     node,
                     parser,
                     selector['rule'],
                     selector['child'],
                     selector['child_value'])

    selected_nodes = new_roots
  
  return selected_nodes


# Base class for Selectors
class Selector:
  def _select(self, root, parser):
    """method for selecting nodes

    :param root: object, root of tree to search
    :param parser: object, parser that built the tree
    :return: list, list of nodes that were selected
    """
    raise Exception('Unimplemented _select method')

  def apply(self, root, parser):
    return self._select(root, parser)


# Selector which returns specified arg value node of specified component
class ComponentArgSelector(Selector):
  def __init__(self, component_name, arg_name):
    self._component_name = component_name
    self._arg_name = arg_name
  
  def _select(self, root, parser):
    return selectPath(
      root,
      parser,
      [{
        # target component
        'rule': 'declaration',
        'child': 'IDENT',
        'child_value': self._component_name
      },
      {
        # target argument
        'rule': 'element_modification',
        'child': 'name',
        'child_value': self._arg_name
      },
      {
        # argument value
        'rule': 'expression',
        'child': None,
        'child_value': None
      }]
    )
