from collections import namedtuple
import time

from antlr4 import *

from modelicaTransformer.Edit import Edit
from modelicaTransformer.modelicaAntlr.modelicaLexer import modelicaLexer
from modelicaTransformer.modelicaAntlr.modelicaParser import modelicaParser

# Collects transformations and applies them to files
class Transformer:
  """Transformer collects transformations and applies them to files"""
  _transformations = []
  _edits = []
  
  def add(self, transformation):
    """add adds a transformation to be applied

    :param transformation: Transformation
    """
    self._transformations.append(transformation)
  
  def _buildEdits(self, tree, parser):
    """_buildEdits generates edits on nodes by applying selectors

    :param tree: object, a node from Antlr AST
    :param parser: object, modelica parser
    """
    self._edits = []

    for trans in self._transformations:
      selected_nodes = trans.selector.apply(tree, parser)
      for node in selected_nodes:
        self._edits.append(trans.edit(node))
  
  def execute(self, source):
    """execute applies transformations to a file and returns the result as a string

    :param source: string, path to file to transform
    :return: string, transformed source
    """
    start = time.time()
    fs = FileStream(source)
    lexer = modelicaLexer(fs)
    stream = CommonTokenStream(lexer)
    parser = modelicaParser(stream)
    tree = parser.stored_definition()
    print(f'build parser: {time.time() - start}')

    start = time.time()
    self._buildEdits(tree, parser)
    print(f'build edits: {time.time() - start}')

    # sort and apply edits in reverse to avoid changing token offsets
    # in the edited file
    self._edits.sort()
    with open(source, 'r') as f:
      return Edit.applyEdits(
        reversed(self._edits),
        f.read())
