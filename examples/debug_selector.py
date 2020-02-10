# This example demonstrates how you can use a selector's debug method to gain
# insight into the nodes it's selecting and what nodes you can select after

# use the custom selector from custom_selector.py example
from custom_selector import ComponentDeclarationSelector

selector = ComponentDeclarationSelector('DC')
selector.debug('DCMotor.mo')