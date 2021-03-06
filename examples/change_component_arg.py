# This example changes the initialization of the ElectroMechanicalElement "EM"
# argument "k"

from modelicaTransformer.Transformation import ReplaceComponentArgumentValue
from modelicaTransformer.Transformer import Transformer

def main():
  transformation = ReplaceComponentArgumentValue("EM", "k", "8")
  transformer = Transformer()
  transformer.add(transformation)

  result = transformer.execute('DCMotor.mo')

  print("Transformed .mo file:")
  print(result)


if __name__ == '__main__':
  main()