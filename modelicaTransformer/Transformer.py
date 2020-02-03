from collections import namedtuple

from antlr4 import *

from modelicaTransformer.Edit import Edit
from modelicaTransformer.modelicaAntlr.modelicaLexer import modelicaLexer
from modelicaTransformer.modelicaAntlr.modelicaParser import modelicaParser

# abstraction of specific nodes and the changes to those nodes
# selector indicates which nodes to apply the change to
# edit indicates the change to apply
Transformation = namedtuple('Transformation', ['selector', 'edit'])

# Collects transformations and applies them to files
class Transformer:
  _transformations = []
  _edits = []
  
  def add(self, transformation):
    """add a transformation

    :param transformation: Transformation
    """
    self._transformations.append(transformation)
  
  def _buildEdits(self, tree, parser):
    """Generates edits on nodes from selectors

    :param tree: object, a node from Antlr AST
    :param parser: object, modelica parser
    """
    self._edits = []

    for trans in self._transformations:
      selected_nodes = trans.selector.apply(tree, parser)
      for node in selected_nodes:
        self._edits.append(trans.edit(node))
  
  def execute(self, source):
    """applies transformations to a file and returns it as a string

    :param source: string, path to file to transform
    :return: string, transformed source
    """
    fs = FileStream(source)
    lexer = modelicaLexer(fs)
    stream = CommonTokenStream(lexer)
    parser = modelicaParser(stream)
    tree = parser.stored_definition()

    self._buildEdits(tree, parser)

    # sort and apply edits in reverse to avoid changing token offsets
    # in the edited file
    self._edits.sort()
    with open(source, 'r') as f:
      return Edit.applyEdits(
        reversed(self._edits),
        f.read()
      )
