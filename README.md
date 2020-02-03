# Modelica Transformer
Package for parsing and transforming Modelica documents.

## Setup
```bash
# install requirements
pip install -r requirements.txt
```

NOTE: if you change the source grammar file you need to regenerate the parser and lexer:
Install antlr4 following [these instructions](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md#installation)
```bash
# in modelicaTransformer/modelicaAntlr
antlr4 -Dlanguage=Python3 modelica.g4
```

## Usage
Transformations are created by defining selectors and edits. Selectors specify how to select nodes in the AST, and edits are modifications (insert, replace, delete) to the text of selected nodes.
Transformer is a collection of transformations, which can then be applied to a file.

### example
This example replaces the initialization value of argument "VAir" of a component named "thermalZoneTwoElements"
```python
import sys

from modelicaTransformer import Transformer, Transformation, Edit, Selector
from modelicaTransformer.Selector import ComponentArgSelector

# get the modelica file name
source = sys.argv[1]

# select the component arg and replace the value with 54321
select_VAir = ComponentArgSelector('thermalZoneTwoElements', 'VAir')
edit_VAir = Edit.makeReplace('54321')
transform_VAir = Transformation(select_VAir, edit_VAir)

t = Transformer()
t.add(transform_VAir)

# run transformations on the source file and write the result to file
res = t.execute(source)
with open('edited_1.mo', 'w') as f:
  f.write(res)
```