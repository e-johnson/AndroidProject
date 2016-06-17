""" This module provides access to the audio that is loaded in FaceFX Studio.

classes:

LinkFunctionParameter -- a named float used in the InputLink
InputLink -- a link from another node to the current node
UserProperty -- a user-configurable property on a node
Node -- a node in the FaceGraph that operates on the inputs
FaceGraph -- a collection of nodes in a directed acyclic graph

Owner: Jamie Redmond

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from FxStudio import getFaceGraphNodeNames, getFaceGraphNodeProperties


class LinkFunctionParameter(object):
    """ A named parameter in a link function.

    instance variables:
    name -- the name of the parameter
    value -- the float value of the parameter

    """

    def __init__(self, linkFunctionParameterTupleFromStudio):
        """ Initialize the object with the tuple from Studio. """
        self.name, self.value = linkFunctionParameterTupleFromStudio

    def __str__(self):
        """ Returns the string representation of the LinkFunctionParameter """
        return 'name={0}  value={1}'.format(self.name, self.value)

    def __repr__(self):
        """ Returns the Python representation of the LinkFunctionParameter """
        return 'LinkFunctionParameter(({0}, {1}))'.format(self.name, self.value)


class InputLink(object):
    """ A link between two face graph nodes.

    instance variables:

    name -- the name of the node from which the input will come
    linkFunctionName -- the name of the link function to transform the value
    linkFunctionParameters -- a list of the named parameters to the link fn

    """

    def __init__(self, nodeInputTupleFromStudio):
        """ Initializes the object with the tuple from Studio """
        self.name = nodeInputTupleFromStudio[0]
        self.linkFunctionName = nodeInputTupleFromStudio[1]
        self.linkFunctionParameters = [LinkFunctionParameter(p)
            for p in nodeInputTupleFromStudio[2]]

    def getNumLinkFunctionParameters(self):
        """ Returns the number of link function parameters. """
        return len(self.linkFunctionParameters)

    def __str__(self):
        """ Returns the string representation of the InputLink. """
        return 'name={0}  linkFunctionName={1}'.format(self.name,
            self.linkFunctionName)


class UserProperty(object):
    """ A user property attached to a Face Graph node.

    instance variables:
    name -- the name of the user property
    type -- the type of the user property
    value -- the value of the user property

    """

    def __init__(self, userPropertyTupleFromStudio):
        """ Initialies the object with the tuple from Studio. """
        self.name = userPropertyTupleFromStudio[0]
        self.type = userPropertyTupleFromStudio[1]
        self.value = userPropertyTupleFromStudio[2]

    def __str__(self):
        """ Returns the string representation of the UserProperty. """
        return 'name={0}  type={1}  value={2}'.format(self.name, self.type,
            self.value)


class Node(object):
    """ A node in the Face Graph.

    instance variables

    faceGraph -- the FaceGraph object that contains this node
    name -- the name of the Face Graph node
    type -- the type of the node
    range -- the valid range of node values as a tuple (min, max)
    inputOperation -- the operation performed to combine the node's inputs
    inputs -- a list of the InputLink objects that define the node's connections
    outputs -- a list of the names of the nodes the object outputs to
    userProperties -- a list of the UserProperty objects attached to the node

    """

    def __init__(self, name, nodeTupleFromStudio, faceGraph):
        """ Initializes the node with the tuple from Studio. """
        self.faceGraph = faceGraph
        self.name = name
        self.type = nodeTupleFromStudio[0]
        self.range = nodeTupleFromStudio[1]
        self.inputOperation = nodeTupleFromStudio[2]
        self.inputs = [InputLink(i) for i in nodeTupleFromStudio[3]]
        self.outputs = []
        self.userProperties = [UserProperty(p) for p in nodeTupleFromStudio[4]]

    def getNumInputs(self):
        """ Returns the number of inputs to the node. """
        return len(self.inputs)

    def getNumOutputs(self):
        """ Returns the number of outputs from the node. """
        return len(self.outputs)

    def hasInput(self, nodeName):
        """ Returns True if the node has an input from the named node.

        named arguments:
        nodeName -- the node name to search the input links for
        """
        return any(input.name == nodeName for input in self.inputs)

    def hasOutput(self, nodeName):
        """ Returns True if the node has an output to the named node.

        named arguments:
        nodeName -- the node name to search the outputs for
        """
        return nodeName in self.outputs

    def isInfluencedBy(self, nodeName):
        """ Returns True if this node is influenced by the named node.

        If True is returned the node named 'nodeName' is connected via its
        outputs to this node in some way. There could be multiple nodes and
        links between 'nodeName' and this node.

        named arguments:
        nodeName -- the node name to search the graph for
        """
        if self.hasInput(nodeName):
            return True
        else:
            return any(
                self.faceGraph.findNode(input.name).isInfluencedBy(nodeName) for
                input in self.inputs)

    def influences(self, nodeName):
        """ Returns True if this node influences the named node.

        If True is returned this node is connected to the node named 'nodeName'
        via its outputs in some way. There could be multiple nodes and links
        between this ndoe and 'nodeName'
        """
        if self.hasOutput(nodeName):
            return True
        else:
            return any(
                self.faceGraph.findNode(output).influences(nodeName) for
                output in self.outputs)

    def __str__(self):
        """ Returns the string representation of the Node. """
        r = self.name + ":\n"
        r += "        type: " + self.type + "\n"
        r += "        range: " + str(self.range[0]) + ", " + str(self.range[1]) + "\n"
        r += "        inputOperation: " + self.inputOperation + "\n"
        r += "        " + str(self.getNumInputs()) + " input(s):\n"
        inputIndex = 0
        for input in self.inputs:
            r += "                [" + str(inputIndex) + "] " + input.name + ", " + input.linkFunctionName + ", " + str(input.getNumLinkFunctionParameters()) + " params:\n"
            paramIndex = 0
            for param in input.linkFunctionParameters:
                r += "                                [" + str(paramIndex) + "] " + param.name + " = " + str(param.value) + "\n"
                paramIndex += 1
            inputIndex += 1
        r += "        " + str(self.getNumOutputs()) + " output(s):\n"
        outputIndex = 0
        for output in self.outputs:
            r += "                [" + str(outputIndex) + "] " + output + "\n"
            outputIndex += 1
        r += "        " + str(self.getNumUserProperties()) + " user properties:\n"
        userPropertyIndex = 0
        for userProperty in self.userProperties:
            r += "                [" + str(userPropertyIndex) + "] " + userProperty.type + ": " + userProperty.name + " = " + userProperty.value + "\n"
            userPropertyIndex += 1
        return r

    def isConnectedTo(self, nodeName):
        """ Returns True if there is any connection between this and the named
        node. """
        return self.isInfluencedBy(nodeName) or self.influences(nodeName)

    def getNumUserProperties(self):
        """ Returns the number of user properties attached to the node. """
        return len(self.userProperties)


class FaceGraph(object):
    """ A directed acyclic graph of Nodes connected by InputLinks

    instance variables:

    nodes -- a list of Node objects

    """

    def __init__(self):
        nodeNames = getFaceGraphNodeNames()
        self.nodes = [Node(n, getFaceGraphNodeProperties(n), self) for n in
            nodeNames]
        for node in self.nodes:
            for input in node.inputs:
                self.findNode(input.name).outputs.append(node.name)

    def getNumNodes(self):
        """ Returns the number of nodes in the Face Graph """
        return len(self.nodes)

    def findNode(self, nodeName):
        """ Returns the node with the given name, or None if not found """
        for node in self.nodes:
            if node.name == nodeName:
                return node
        return None

    def __str__(self):
        """ Returns the string representation of the face graph. """
        r = '{0} nodes:\n'.format(self.getNumNodes())
        r += '\n'.join(['[{0}] {1}'.format(index, node) for index, node in
            enumerate(self.nodes)])
        return r
