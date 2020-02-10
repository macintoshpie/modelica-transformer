
from antlr4 import *
from antlr4.xpath import XPath

from modelicaTransformer.modelicaAntlr.modelicaLexer import modelicaLexer
from modelicaTransformer.modelicaAntlr.modelicaParser import modelicaParser


def select(root, parser, rule, child=None, child_value=None):
  """select selects the rule in AST that has a child with child_value
  If child is None, then it just returns the matched rule nodes
  e.g. select a component declaration whose identifier is thermalZoneTwoElements

  :param root: object, tree to search
  :param parser: object, parser that generated the tree
  :param rule: string, name of node to search for
  :param child: string, (optional) name of direct descendant used to filter nodes by inspecting it's text
  :param child_value: (optional) string, value to match text to
  """
  matches = XPath.XPath.findAll(root, f'//{rule}', parser)
  if len(matches) == 0:
    return []
  
  # check if we need to do filtering
  if child == None:
    return matches

  def child_missing():
    return []

  results = []
  for match in matches:
    # this works b/c nodes of AST are ParserRuleContext, and calling child node
    # as a method returns that context
    children = getattr(match, child, child_missing)()

    # possible for match to have multiple children of the same type
    # e.g. connect_clause has two component_reference, so treat result as a list
    if not isinstance(children, list):
      children = [children]
    
    # filter this match based on child condition
    for _child in children:
      val = _child.getText()
      if val == child_value:
        results.append(match)
  
  return results
  

def selectPath(root, parser, path):
  """selectPath selects nodes based on a series of node selectors

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
  """Selector is the base class for all selectors"""
  _chained_selector = None

  def _select(self, root, parser):
    """_select should be overridden when implementing a Selector

    :param root: object, root of tree to search
    :param parser: object, parser that built the tree
    :return: list, list of nodes that were selected
    """
    raise Exception('Unimplemented _select method')

  def apply(self, root, parser):
    """apply runs selector as well as any chained selectors

    :param root: object, root of tree to search
    :param parser: object, parser that built the tree
    :return: list, list of nodes that were selected
    """
    # pylint: disable=assignment-from-no-return
    selected_nodes = self._select(root, parser)
    if not self._chained_selector:
      return selected_nodes
    
    selected_and_chained_nodes = []
    for node in selected_nodes:
      selected_and_chained_nodes += self._chained_selector.apply(node, parser)
    
    return selected_and_chained_nodes
  
  def chain(self, selector):
    """chain chains a selector after this one

    :param selector: object, selector to chain after this one is applied
    :return: object, returns self
    """
    if self._chained_selector == None:
      self._chained_selector = selector
    else:
      self._chained_selector.chain(selector)

    return self
  
  def debug(self, source):
    """debug applies the selector to the source file and prints selected nodes
    
    :param source: string, path to file
    """
    fs = FileStream(source)
    lexer = modelicaLexer(fs)
    stream = CommonTokenStream(lexer)
    parser = modelicaParser(stream)
    tree = parser.stored_definition()

    # pylint: disable=assignment-from-no-return
    matched = self._select(tree, parser)
    self._printDebug(matched)
  
  def _printDebug(self, nodes):
    """_printDebug prints nodes and their children to help debug the selector

    :param nodes: list, nodes to print out (should be the nodes selected)
    """
    def format_node_name(name):
      name = name.lower()
      return name[:-7] if name.endswith("context") else name
    
    # print the selector name
    print(self.__class__.__name__)
    for node in nodes:      
      print(f'  {format_node_name(node.__class__.__name__)}')

      # gather the node's children names and their contents
      child_node_names = []
      child_node_contents = []
      for child in node.children:
        child_content = child.getText()
        child_content = (child_content[:35] + '..') if len(child_content) > 35 else child_content

        child_name = format_node_name(child.__class__.__name__)

        info_len = max(len(child_content), len(child_name))
        child_name = child_name.ljust(info_len, ' ')
        child_content = child_content.ljust(info_len, ' ')

        child_node_names.append(child_name)
        child_node_contents.append(child_content)
      
      # print the node's children
      print(f'    {" | ".join(child_node_names)}')
      print(f'    {" | ".join(child_node_contents)}')


class ComponentArgSelector(Selector):
  """ComponentArgSelector is a Selector which returns the argument assignment
  node on the specified component
  """

  def __init__(self, component_identifier, argument_name):
    """__init__ initializes the selector

    :param component_identifier: string, identifier (ie name) of the component to select
    :param argument_name: string, name of the argument (ie parameter) to select
    """
    self._component_identifier = component_identifier
    self._argument_name = argument_name
  
  def _select(self, root, parser):
    return selectPath(
      root,
      parser,
      [{
        # get component
        'rule': 'declaration',
        'child': 'IDENT',
        'child_value': self._component_identifier
      },
      {
        # get argument
        'rule': 'element_modification',
        'child': 'name',
        'child_value': self._argument_name
      },
      {
        # get argument value
        'rule': 'expression',
        'child': None,
        'child_value': None
      }]
    )

class ConnectSelector(Selector):
  """ConnectSelector is a Selector which returns connect clauses connecting
  component_a and component_b
  """
  def __init__(self, component_a, component_b):
    self._a = component_a
    self._b = component_b
  
  def _select(self, root, parser):
    return selectPath(
      root,
      parser,
      [{
        'rule': 'connect_clause',
        'child': 'component_reference',
        'child_value': self._a
      }]
    )
