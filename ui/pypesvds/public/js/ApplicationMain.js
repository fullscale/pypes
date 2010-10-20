/**
 * Component class
 * @class jsBox
 * @constructor
 */
var jsBox = function(config, layer, ins) {
   
    jsBox.superclass.constructor.call(this, config, layer);
   
    this.buildTextArea(this.config.name || this.config.filterName);
    this.nParams = this.config.inputs.length;
    this.numOuts = this.config.outputs.length;

    this.createTerminals(this.config.inputs, this.config.outputs, this.config.cid);
   
    /* Reposition the terminals when the jsBox is being resized */
    this.ddResize.eventResize.subscribe(function(e, args) {
      this.positionTerminals();
      YAHOO.util.Dom.setStyle(this.textarea, "height", (args[0][1]-30)+"px");
   }, this, true);
};

YAHOO.extend(jsBox, WireIt.Container, { 
   /**
    * Create the textarea for the component label
    */
    buildTextArea: function(codeText) {

        this.textarea = WireIt.cn('textarea', {}, {overflow:'hidden', 
		                                           textAlign:'center', 
												   width: "100%", 
												   height: "30px", 
												   border: "0", 
												   padding: "5px", 
												   backgroundColor: "#ffffff", 
												   resize: "none"}, 
											       codeText);
        this.setBody(this.textarea);
		
		/* Code here can be used to set titles on the component windows.
		 * It's disabled for the time being because I'm not sure I like
		 * the way it looks in the UI.
        this.title = WireIt.cn('span', {}, {color:"#FFFFFF", 
		                                     border:"none", 
											 fontSize:".8em", 
											 fontWeight:"100", 
											 paddingLeft:"5px", 
											 paddingBottom:"0px"}, 
											 this.config.filterName);
        this.setTitle(this.title); */
    },
   
    /**
     * Create (and re-create) the terminals with this.nParams input terminals
     */
    createTerminals: function(inputs, outputs, cid) {

   	    /* Remove all the existing terminals */
   	    this.removeAllTerminals();
		
		/* port ids for tooltip object */
		var ports = new Array();

        for(var i = 0 ; i < inputs.length ; i++) {
            /* add term name here */
            var term = this.addTerminal({xtype: "WireIt.util.TerminalInput", termid:inputs[i], nMaxWires:1 });
            term.jsBox = this;
			var xid = cid.toString() + "in" + i.toString()
            WireIt.sn(term.el, {id:xid, title:inputs[i]}, {position: "absolute", top: "-15px"});
			ports.push(xid);
        }
		
        for(var i = 0; i < outputs.length; i++) {
            /* add term name here */
   	        var term = this.addTerminal({xtype: "WireIt.util.TerminalOutput", termid:outputs[i], nMaxWires:1});      
            term.jsBox = this;
			var xid = cid.toString() + "out" + i.toString()
            WireIt.sn(term.el, {id:xid, title:outputs[i]}, {position: "absolute", bottom: "-15px"});
			ports.push(xid);
        }
		
		/* create the tooltip object */
		new YAHOO.widget.Tooltip("ttPorts", {
			context:ports,
			effect:{effect:YAHOO.widget.ContainerEffect.FADE,duration:0.20},
			zIndex:50
		});
		
        this.positionTerminals();

        /* Declare the new terminals to the drag'n drop handler 
         * (so the wires are moved around with the container)
         */
        this.dd.setTerminals(this.terminals);
    },
   
    /**
     * Reposition the terminals
     */
    positionTerminals: function() {
        /* Calculate the width */
        var widthStr = YAHOO.util.Dom.getStyle(this.el, 'width');
        var width = parseInt( widthStr.substr(0,widthStr.length-2), 10);
        var inputsIntervall = Math.floor(width/(this.nParams+1));
        var outputsIntervall = Math.floor(width/(this.numOuts + 1)); 
      
        for(var i = 0 ; i < this.nParams ; i++) {
            YAHOO.util.Dom.setStyle(this.terminals[i].el, "left", (inputsIntervall*(i+1))-15+"px" );
         
            for(var j = 0 ; j < this.terminals[i].wires.length ; j++) {
                this.terminals[i].wires[j].redraw();
            }
        }
        var offsetIndex = 0;
        for(var i = this.terminals.length-1 ; i > this.nParams-1 ; i--) {
            YAHOO.util.Dom.setStyle(this.terminals[i].el, "left", (outputsIntervall*(offsetIndex+1))-15+"px" );
            offsetIndex = offsetIndex + 1;
         
            for(var j = 0 ; j < this.terminals[i].wires.length ; j++) {
                this.terminals[i].wires[j].redraw();
            }
        }
    },
  
    getConfig: function() {
        var obj = jsBox.superclass.getConfig.call(this);
        /* add custom configuration properties */
        obj.filterName = this.config.filterName;
        obj.name = this.textarea.value;
        obj.type = this.config.type;
        obj.cid = this.config.cid;
        obj.inputs = this.config.inputs;
        obj.outputs = this.config.outputs;
        obj.params = this.config.params;
        return obj;
    },
    
    configComponent: function(component_id, config) {
        var componentConfigHandler = {
            success: function(oResponse) {
				var params = YAHOO.lang.JSON.parse(oResponse.responseText);
				if (params != "null") {
					config.params = params;
					var formString = "";
					
					for (param in params) {
						value = params[param][0];
						options = params[param][1];
						if (options.length == 0) {
							formString += '\
							<p>\
							<label style="width:4em;\
							              float:left;\
										  margin-right:0.5em;\
										  display:block;" for=\"'+param+'\">' 
							  + param + 
							':</label><br>\
							<input type="text"\
							       id="'+param+'"\
								   size="40" \
								   name="'+param+'"\
								   value="'+value+'">\
							</p><br />'
						}
						else {
							optString = '<select name="' +param+ '">'
							for (index in options) {
								opt = options[index];
								if (opt === value) {
									optString += '<option value="'+opt+'" selected>' + opt;
								}
								else {
									optString += '<option value="'+opt+'">' + opt;
								}
							}
							optString += "</select>"
							formString += '\
							<p>\
							<label style="width:4em;\
							       float:left;\
							       margin-right:0.5em;\
							       display:block;" for="'+param+'">' 
								+ param + 
							':</label><br>'+optString+'</p><br />'
						}
					}
				}
                ConfigPanel = new YAHOO.widget.Dialog("configDialog", { 
				    width: "390px",
                    zIndex: 25,
                    modal: true,
                    fixedcenter: true, 
                    visible: false, 
                    draggable: true, 
                    close: true,
                    constraintoviewport: true,
                    buttons: [{ text:"OK", handler:SubmitConfig },
                              { text:"Cancel", handler:handleCancel } 
                    ]
                });
                
                var thisType = config.type.substring(0, config.type.length -1)
                ConfigPanel.setHeader("Configure Component (" + thisType + "): " + config.filterName);
                ConfigPanel.argument = config;

                /* if params was null then the backend could not find the  
                 * specified component. This likely means that the browser
                 * cache is out of sync with what the server has.
                 */
                if (params === "null") {
					ConfigPanel.setBody('\
					<img src="images/config_banner.png"/><br/><br>\
					<p>We were unable to locate this component on the\
					   server. This likely measn that you are working with a stale\
					   browser cache. Refresh your browser window and try again.\
					</p><br/>');
					
                /* An empty formstring simply means the component doesn't
                 * specify any configurable parameters.
                 */
				} else if (formString === "") {
					ConfigPanel.setBody('\
					<img src="images/config_banner.png"/><br/><br>\
					<p>This component has no configurable parameters.</p><br/>');
					
				/* We got a valid reponse from the server and this
				 * component offers configurable parameters. Show em.
				 */
				} else {
                    ConfigPanel.setBody('\
					<img src=\"images/config_banner.png\"/><br/><br>\
					<form method="POST" action="/filters/'+component_id+'" id="ConfigForm">'
					+ formString + 
					'<br><input type="hidden" name="_method" value="PUT"/></form>');
                }

                ConfigPanel.cfg.setProperty("zIndex", 25);
                ConfigPanel.render(document.body);
                ConfigPanel.cfg.setProperty("zIndex", 25);
                ConfigPanel.show();
            },

            failure: function(oResponse) {
            }            
        };
        YAHOO.util.Connect.asyncRequest('GET', 'filters/' + component_id, componentConfigHandler);
    },

    onCloseButton: function(e, args) {
        /* need to delete instance here */
        var instanceId = args.config.cid;
        YAHOO.util.Event.stopEvent(e);
        this.layer.removeContainer(args);
        YAHOO.util.Connect.asyncRequest('DELETE', 'filters/' + instanceId, callback);
    },

    onConfigButton: function(e, args) {
        var component_id = args.config.cid;
        YAHOO.util.Event.stopEvent(e);
        this.configComponent(component_id, args.config);
    },

    next: function() {
        var obj;
        try {
            obj = this.terminals[1].wires[0].getOtherTerminal(this.terminals[1]).container;
        } catch (error) { }
        return obj;
    }
});

var onSuccess = function(o) { 
    /* catch bad responses due to Webkit (Safari/Chrome)
     * calling submit() without a form (see SubmitConfig)
     */
	try {
		o.argument.params = YAHOO.lang.JSON.parse(o.responseText);
	} catch(error) { /* we can safely swallow the error */ }
}
var onFailure = function(o) { alert("Your submission failed. Status: " + o.status); } 

/* config submission handler */
var SubmitConfig = function(e, args) { 
    this.callback.success = onSuccess;
	this.callback.failure = onFailure;
    this.callback.argument = args.argument;
	
	/* Firefox will throw an exception if there
	 * is not an actual form to submit. This is the
	 * case when a component has no parameters. Webkit
	 * (Safari/Chrome) will still call submit() and
	 * hide the dialog window.
	 */
	try {
		this.submit();
	} catch(err) { this.cancel(); }
}

var callback = {};
var handleOk = function() { this.hide(); };
/* handles config cancel button */
var handleCancel = function() { this.cancel(); }

/**
 * Saves (registers) a project configuration created in the UI
 * on the backend server.
 * 
 * TODO: I think we have a DOM leak here in continually
 * creating the simple dialog.
 */
jsBox.register = function() {
	/* get the local configuration */
    var config = YAHOO.lang.JSON.stringify(jsBox.jsBoxLayer.getWiring());
    var postData = "config=" + escape(config);

    var registerHandler = {
		/* called upon successfully saving the project */
        success: function(oResponse) {
           regPanel = new YAHOO.widget.SimpleDialog("registerdialog",  
                { width: "300px",
                zIndex: 25,
                modal: true,
                fixedcenter: true, 
                visible: false, 
                draggable: true, 
                close: true, 
                text: oResponse.responseText,
                icon: YAHOO.widget.SimpleDialog.ICON_INFO,
                constraintoviewport: true, 
                buttons: [{ text:"OK", handler:handleOk}] 
            });

         regPanel.setHeader("Register Workflow"); 
         regPanel.render(document.body);
         regPanel.show();
        },

        /* called when the project is unabe to be saved */
        failure: function(oResponse) {
            regPanel = new YAHOO.widget.SimpleDialog("registerdialog",  
                { width: "300px",
                zIndex: 25,
                fixedcenter: true, 
                visible: false, 
                draggable: true, 
                close: true, 
                text: "An Unidentified Error Has Ocurred",
                icon: YAHOO.widget.SimpleDialog.ICON_ERROR, 
                constraintoviewport: true, 
                buttons: [{ text:"OK", handler:handleOk}] 
            });

         regPanel.setHeader("Register Workflow"); 
         regPanel.render(document.body);
         regPanel.show();
        }
    };
	/* send the configuration to the server */
    YAHOO.util.Connect.asyncRequest('POST', '/project', registerHandler, postData);
};

/**
 * Adds a component to the canvas layer
 */
jsBox.addModule = function (filterName, type, xpos, ypos) {
    /* Need to call backend here and get inputs/outputs and create instance */
    var callback = {
        success: function(oResponse) {
			var resultArray = YAHOO.lang.JSON.parse(oResponse.responseText)
            var compId = resultArray[0];

            /* We don't show input ports on input adapters 
             * but technically they're still needed in pypes
             * core to be able to send data into the graph.
             * Here we're just hiding them in the javascript.
             */
            if (type === "Adapters") {
                var ins = [];
            } else {
                var ins = resultArray[1];
            }

            /* We don't show output ports on publishers.
             * A proper component would remove any output
             * ports but folks could forget to remove them
             * so here we're just hiding any if they exist.
             */
            if (type === "Publishers") {
                var outs = [];
            } else {
                var outs = resultArray[2];
            }
			
			/* add the component to the canvas */
            jsBox.jsBoxLayer.addContainer({
				"filterName": filterName, 
				"type":type, 
				"cid":compId, 
				xtype: "jsBox", 
				"inputs":ins, 
				"outputs":outs, 
				"position":[xpos, ypos]
			});
        },
        failure: function(oResponse) {
            oResponse.argument.fnLoadComplete();
        },
        timeout: 7000
    };
	/* create an instance of the component on the server */
    var postData = "klass=" + filterName;
    YAHOO.util.Connect.asyncRequest("POST", "/filters", callback, postData);
};

/**
 * Initialize the application
 */
YAHOO.util.Event.addListener(window, "load", function() {
	/* create the app layout */
	YAHOO.pypes.ui.layout.Window.init();
	
	/* create the app tree */
	YAHOO.pypes.ui.tree.AppTree.init();
 
    /* setup the canvas layer */
    var tag = document.getElementById('wirelayer');
    jsBox.jsBoxLayer = new WireIt.Layer({layerMap: true, parentEl: tag});
	
	/* create the drag-n-drop target on the canvas layer */
    new YAHOO.util.DDTarget(jsBox.jsBoxLayer.el, "components");

    /* callback used to handle response from /project/current */
    var get_project_callback = {
        success: function(oResponse) {
            jsBox.jsBoxLayer.setWiring(YAHOO.lang.JSON.parse(oResponse.responseText));
        },
        failure: function(oResponse) {},
        timeout: 7000
    };
	/* get the current project from the server */
    YAHOO.util.Connect.asyncRequest("GET", "/project/current", get_project_callback);
});


