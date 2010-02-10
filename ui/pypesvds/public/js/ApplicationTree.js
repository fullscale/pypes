/**
 * The ApplicationTree module controls the creation of the
 * component tree. It provides animation when expanding and
 * collapsing tree nodes. It also caches its items so that
 * on each operation it does not have to callback to the server
 * for a list of valid components.
 * 
 * @module ApplicationTree
 * @requires dom, event, layout
 */
YAHOO.namespace("pypes.ui.tree");

YAHOO.pypes.ui.tree.AppTree = function () {
	
	var tree, currentIconMode;
	
	DDTreeNode = function(id, sGroup, config) {
        DDTreeNode.superclass.constructor.call(this, id, sGroup, config);
    };

    YAHOO.extend(DDTreeNode, YAHOO.util.DDProxy, {
        /* don't actually move anything */
        endDrag: function(e) { },

        /* this will trigger the component creation */
        onDragDrop: function(e, id) {
            var xcoord = YAHOO.util.Event.getPageX(e) - 200;
            var ycoord = YAHOO.util.Event.getPageY(e) - 70;
            jsBox.addModule(this.config.label, this.config.type, xcoord, ycoord);
        }
    });

    function changeIconMode() {
        var newVal = parseInt(this.value);
        if (newVal != currentIconMode) {
            currentIconMode = newVal;
        }
        buildTree();
    }
    
    function loadNodeData(node, fnLoadComplete)  {
            
        /* We'll load node data based on what we get back when we
         * use Connection Manager topass the text label of the 
         * expanding node to the Yahoo!
         * Search "related suggestions" API.  Here, we're at the 
         * first part of the request -- we'll make the request to the
         * server.  In our success handler, we'll build our new children
         * and then return fnLoadComplete back to the tree.
         */
            
        /* Get the node's label and urlencode it; this is the word/s
         * on which we'll search for related words:
         */
        var nodeLabel = encodeURI(node.label);
            
        /* prepare URL for XHR request: */
        var sUrl = "/filters?node=" + nodeLabel;
            
        /* prepare our callback object */
        var callback = {
            /* if our XHR call is successful, we want to make use
             * of the returned data and create child nodes.
             */
            success: function(oResponse) {
				var x = YAHOO.lang.JSON.parse(oResponse.responseText);
                for (i = 0; i < x.length; i++) {
                    var tempNode = new YAHOO.widget.HTMLNode({html:"<div id='tnode_" + x[i] + "' style='cursor:default;'>" + x[i] + "</div>"}, node, false); // was TextNode
                    tempNode.label = x[i];
                    tempNode.type = nodeLabel;
                    tempNode.isLeaf = true;
                    var dd = new DDTreeNode("tnode_" + x[i], "components", {"label": x[i], "type": nodeLabel, dragElId:"proxy", resizeFrame: false});
                }
                    
                /* When we're done creating child nodes, we execute the node's
                 * loadComplete callback method which comes in via the argument
                 * in the response object (we could also access it at node.loadComplete,
                 * if necessary):
                 */
                oResponse.argument.fnLoadComplete();
                   
            },
                
            /* if our XHR call is not successful, we want to
             * fire the TreeView callback and let the Tree
             * proceed with its business.
             */
            failure: function(oResponse) {
                oResponse.argument.fnLoadComplete();
            },
                
            /* our handlers for the XHR response will need the same
             * argument information we got to loadNodeData, so
             * we'll pass those along:
             */
            argument: {
                "node": node,
                "fnLoadComplete": fnLoadComplete
            },
                
            /* timeout -- if more than 7 seconds go by, we'll abort
             * the transaction and assume there are no children:
             */
            timeout: 7000
        };
            
        /* With our callback object ready, it's now time to 
         * make our XHR call using Connection Manager's
         * asyncRequest method:
         */
        YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
    }

    function buildTree() {
       /* create a new tree: */
       tree = new YAHOO.widget.TreeView("tree");

       /* set tree expand/collapse animation */
       tree.setExpandAnim(YAHOO.widget.TVAnim.FADE_IN);
       tree.setCollapseAnim(YAHOO.widget.TVAnim.FADE_OUT);
           
       /* turn dynamic loading on for entire tree: */
       tree.setDynamicLoad(loadNodeData, currentIconMode);
           
       /* get root node for tree: */
       var root = tree.getRoot();
           
       /* add child nodes for tree */
       var aStates = ["Adapters","Transformers","Filters","Operators","Extractors","Publishers"];
           
       for (var i=0, j=aStates.length; i<j; i++) {
            var tempNode = new YAHOO.widget.TextNode(aStates[i], root, false);
       }
           
       /* render tree with these toplevel nodes; all descendants of these node
        * will be generated as needed by the dynamoader.
        */
       tree.draw();

        tree.subscribe("dblClickEvent", function(oArgs) {
            jsBox.addModule(oArgs.node.label, oArgs.node.type, 100, 100); 
        });
    }

    return {
        init: function() {
            YAHOO.util.Event.on(["mode0", "mode1"], "click", changeIconMode);
            var el = document.getElementById("mode1");
            if (el && el.checked) {
                currentIconMode = parseInt(el.value);
            } else {
                currentIconMode = 0;
            }
            buildTree();
        } 
    }
}(); 


