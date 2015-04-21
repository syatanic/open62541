#!/usr/bin/env/python
# -*- coding: utf-8 -*-

###
### Author:  Chris Iatrou (ichrispa@core-vector.net)
### Version: rev 13
###
### This program was created for educational purposes and is released into the
### public domain under the General Public Licence. A copy of the GNU GPL is
### available under http://www.gnu.org/licenses/gpl-3.0.html.
###
### This program is not meant to be used in a production environment. The
### author is not liable for any complications arising due to the use of
### this program.
###

from logger import *
from ua_constants import *

__unique_item_id = 0

class open62541_MacroHelper():
  def __init__(self):
    pass

  def getCreateExpandedNodeIDMacro(self, node):
    if node.id().i != None:
      return "UA_EXPANDEDNODEID_NUMERIC(" + str(node.id().ns) + ", " + str(node.id().i) + ")"
    elif node.id().s != None:
      return "UA_EXPANDEDNODEID_STRING("  + str(node.id().ns) + ", " + node.id().s + ")"
    elif node.id().b != None:
      log(self, "NodeID Generation macro for bytestrings has not been implemented.")
      return ""
    elif node.id().g != None:
      log(self, "NodeID Generation macro for guids has not been implemented.")
      return ""
    else:
      return ""

  def getCreateNodeIDMacro(self, node):
    if node.id().i != None:
      return "UA_NODEID_NUMERIC(" + str(node.id().ns) + ", " + str(node.id().i) + ")"
    elif node.id().s != None:
      return "UA_NODEID_STRING("  + str(node.id().ns) + ", " + node.id().s + ")"
    elif node.id().b != None:
      log(self, "NodeID Generation macro for bytestrings has not been implemented.")
      return ""
    elif node.id().g != None:
      log(self, "NodeID Generation macro for guids has not been implemented.")
      return ""
    else:
      return ""

  def getCreateStandaloneReference(self, sourcenode, reference):
  # As reference from open62541 (we need to alter the attributes)
  #    #define ADDREFERENCE(NODEID, REFTYPE_NODEID, TARGET_EXPNODEID) do {     \
  #        UA_AddReferencesItem item;                                      \
  #        UA_AddReferencesItem_init(&item);                               \
  #        item.sourceNodeId = NODEID;                                     \
  #        item.referenceTypeId = REFTYPE_NODEID;                          \
  #        item.isForward = UA_TRUE;                                       \
  #        item.targetNodeId = TARGET_EXPNODEID;                           \
  #        UA_Server_addReference(server, &item);                          \
  #    } while(0)
    code = []
    refid = "ref_" + reference.getCodePrintableID()
    code.append("UA_AddReferencesItem " + refid + ";")
    code.append("UA_AddReferencesItem_init(&" + refid + ");")
    code.append(refid + ".sourceNodeId = " + self.getCreateNodeIDMacro(sourcenode) + ";")
    code.append(refid + ".referenceTypeId = " + self.getCreateNodeIDMacro(reference.referenceType()) + ";")
    if reference.isForward():
      code.append(refid + ".isForward = UA_TRUE;")
    else:
      code.append(refid + ".isForward = UA_FALSE;")
    code.append(refid + ".targetNodeId = " + self.getCreateExpandedNodeIDMacro(reference.target()) + ";")
    code.append("UA_Server_addReference(server, &" + refid + ");")
    return code

  def getCreateNode(self, node):
    nodetype = ""
    code = []

    code.append("// Node: " + str(node) + ", " + str(node.browseName()))

    if node.nodeClass() == NODE_CLASS_OBJECT:
      nodetype = "UA_ObjectNode"
    elif node.nodeClass() == NODE_CLASS_VARIABLE:
      nodetype = "UA_VariableNode"
    elif node.nodeClass() == NODE_CLASS_METHOD:
      nodetype = "UA_MethodNode"
    elif node.nodeClass() == NODE_CLASS_OBJECTTYPE:
      nodetype = "UA_ObjectTypeNode"
    elif node.nodeClass() == NODE_CLASS_REFERENCETYPE:
      nodetype = "UA_ReferenceTypeNode"
    elif node.nodeClass() == NODE_CLASS_VARIABLETYPE:
      nodetype = "UA_VariableTypeNode"
    elif node.nodeClass() == NODE_CLASS_DATATYPE:
      nodetype = "UA_DataTypeNode"
    elif node.nodeClass() == NODE_CLASS_VIEW:
      nodetype = "UA_ViewNode"
    elif node.nodeClass() == NODE_CLASS_METHODTYPE:
      nodetype = "UA_MethodTypeNode"
    else:
      nodetype = "UA_NodeTypeNotFoundorGeneric"

    code.append(nodetype + " *" + node.getCodePrintableID() + " = " + nodetype + "_new();")
    code.append(node.getCodePrintableID() + "->browseName = UA_QUALIFIEDNAME_ALLOC(" +  str(node.id().ns) + ", \"" + node.browseName() + "\");")
    code.append(node.getCodePrintableID() + "->displayName = UA_LOCALIZEDTEXT_ALLOC(\"en_US\", \"" +  node.displayName() + "\");")
    code.append(node.getCodePrintableID() + "->description = UA_LOCALIZEDTEXT_ALLOC(\"en_US\", \"" +  node.description() + "\");")
    code.append(node.getCodePrintableID() + "->writeMask = (UA_Int32) " +  str(node.__node_writeMask__) + ";")
    code.append(node.getCodePrintableID() + "->userWriteMask = (UA_Int32) " + str(node.__node_userWriteMask__) + ";")
    #FIXME: Allocate descriptions, etc.

    if node.id().i != None:
      code.append(node.getCodePrintableID() + "->nodeId.identifier.numeric = " + str(node.id().i) + ";")
    elif node.id().b != None:
      log(self, "ByteString IDs for nodes has not been implemented yet.", LOG_LEVEL_ERROR)
      return []
    elif node.id().g != None:
      #<jpfr> the string is sth like { .length = 111, .data = <ptr> }
      #<jpfr> there you _may_ alloc the <ptr> on the heap
      #<jpfr> for the guid, just set it to {.data1 = 111, .data2 = 2222, ....
      log(self, "GUIDs for nodes has not been implemented yet.", LOG_LEVEL_ERROR)
      return []
    elif node.id().s != None:
      code.append(node.getCodePrintableID() + "->nodeId.identifier.numeric = UA_STRING_ALLOC(\"" + str(node.id().i) + "\");")
    else:
      log(self, "Node ID is not numeric, bytestring, guid or string. I do not know how to create c code for that...", LOG_LEVEL_ERROR)
      return []

    return code
