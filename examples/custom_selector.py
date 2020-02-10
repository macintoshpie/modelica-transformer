# This example demonstrates how to implement a custom Selector and combine it
# with an Edit to make a Transformation that adds an annotation to a component

from modelicaTransformer.Selector import Selector, selectPath
from modelicaTransformer.Edit import Edit
from modelicaTransformer.Transformation import Transformation
from modelicaTransformer.Transformer import Transformer


class ComponentDeclarationSelector(Selector):
  def __init__(self, component_identifier):
    """We'll use component_identifier to select only the component with this ident"""
    self._component_identifier = component_identifier

  def _select(self, root, parser):
    """this is our method which will be called to select and return nodes
    root will be the root of the AST, and parser is the parser that constructed
    the AST
    """

    # selectPath allows us to select nodes from a path
    matched = selectPath(
      root,
      parser,
      [{
        # get declaration that has our identifier
        'rule': 'declaration',
        'child': 'IDENT',
        'child_value': self._component_identifier
      }]
    )

    if len(matched) != 1:
      raise Exception(f'Unable to find component with identifier ${self._component_identifier}')
      
    # the node we need to modify is actually the parent of our matched node, so get the parent
    # the returned value needs to be a list so we wrap it in one here as well
    return [matched[0].parentCtx]


def main():
  # instantiate our Selector to target the component identified as "load"
  selector = ComponentDeclarationSelector("load")

  # create an edit that will insert text after the selected node
  edit = Edit.makeInsert(' "This is a comment for load..."')

  # combine the selector and edit into a transformation
  transformation = Transformation(selector, edit)

  # create a transformer and add the transformation
  transformer = Transformer()
  transformer.add(transformation)

  result = transformer.execute('DCMotor.mo')

  print("Transformed .mo file:")
  print(result)

if __name__ == '__main__':
  main()