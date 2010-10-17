/*YAHOO.namespace("pypes.ui.toolbar");

YAHOO.pypes.ui.toolbar.Window = function() {
    return {
		
	
	};
}();*/

var responseDialog = new YAHOO.widget.SimpleDialog("responseDialog", { 
	width: "300px",
    zIndex: 25,
    fixedcenter: true, 
    visible: false, 
    draggable: true, 
    close: true, 
    constraintoviewport: true, 
    buttons: [{ text:"OK", handler:handleOk}] 
});

var submitMenu = [ 
    { text: 'File', value: 'file', id: 'file_upload' },
	{ text: 'Trigger', value: 'file', id: 'run_trigger' },
    /*{ text: 'Submit URL', value: 'url', id: 'submit_url' }*/
]; 

var Toolbar = function() {
	/* get the toolbar element */
	var logo = YAHOO.util.Dom.get("toolbar");
	
	/* create <span> */
	var span = document.createElement('span');
	
	/* create <a href='/'> */
    var link = document.createElement('a');
    var href = document.createAttribute('href');
    href.nodeValue = '/';
    link.setAttributeNode(href);
	
	/* create <img src="/images/KrupePypeLogo.png"> */
	var img = document.createElement('img');
	var srcAttr = document.createAttribute("src");
    srcAttr.nodeValue = "/images/KrupePypeLogo.png";
    img.setAttributeNode(srcAttr);
	
	/* append all the nodes to the DOM */
	link.appendChild(img);
	span.appendChild(link);
	logo.appendChild(span);
}();

var handleOk = function() {this.hide();};

/* AJAX FILE UPLOAD CODE */
/* create a panel to use */
var UploadPanel = new YAHOO.widget.Panel("UploadWindow", {
    zIndex: 25,
    width:"300px",
    modal: true,
    fixedcenter: true,  
    constraintoviewport: true,  
    close:true,  
    draggable:true
});

var onUploadCancel = function() {UploadPanel.hide();};

/* this will be called when the upload/submit button is clicked */
var onUploadButtonClick = function(e){
    /* the second argument tells Connection Manager this is a file upload form */
    YAHOO.util.Connect.setForm('docsubmit', true);

    var uploadHandler = {
        upload: function(oResponse) {
			var response = YAHOO.lang.JSON.parse(oResponse.responseText)
            responseDialog.setHeader("Submit Document");
			responseDialog.setBody(response.msg);
            responseDialog.render(document.body);
            responseDialog.show();
        }
    };
    YAHOO.util.Connect.asyncRequest('POST', '/data/ui/file', uploadHandler);
    UploadPanel.hide();
};

/* function that dispays the upload dialog */
var UploadDlg = function() {
    UploadPanel.setHeader("Document Submitter"); 
    UploadPanel.setBody( "<p>Select a document for submission and then click the Submit button.</p><br><form method=\"post\" action=\"/docs\" name=\"submit\" enctype=\"multipart/form-data\" id=\"docsubmit\"><input type=\"file\" name=\"document\"><br><br><div style=\"float:right;\"><input type=\"button\" id=\"uploadButton\" name=\"upload\" value=\"Upload\"><button id=\"uCancelButton\" type=\"button\">x</button></div><br></form><br>");
    UploadPanel.setFooter("To cancel this action, select the Cancel button.");
    UploadPanel.render(document.body);
    /* z-index hack */
    UploadPanel.cfg.setProperty("zIndex", 25);
    UploadPanel.cfg.setProperty("width", "400px");
    UploadPanel.cfg.setProperty("fixedcenter", true);

    /* Setup dialog buttons */
    var oSubmitButton = new YAHOO.widget.Button("uploadButton", {label: "Submit", padding: "5px"});
    var oCancelButton = new YAHOO.widget.Button("uCancelButton", {label: "Cancel", padding: "5px"});

    /* show the panel */
    UploadPanel.show();

    /* make sure to register the listener */
    YAHOO.util.Event.addListener('uploadButton', 'click', onUploadButtonClick);
    YAHOO.util.Event.addListener('uCancelButton', 'click', onUploadCancel);
};
/* END AJAX UPLOAD CODE */

/* trigger event handler */
var onTrigger = function(e){
    var triggerHandler = {
        success: function(oResponse) {
			//var response = YAHOO.lang.JSON.parse(oResponse.responseText)
            responseDialog.setHeader("Submit Trigger");
			responseDialog.setBody("Success");
            responseDialog.render(document.body);
            responseDialog.show();
        },
		failure: function(oResponse) {
			var response = YAHOO.lang.JSON.parse(oResponse.responseText)
            responseDialog.setHeader("Submit Trigger");
			responseDialog.setBody(response.error);
            responseDialog.render(document.body);
            responseDialog.show();
		}
    };
    YAHOO.util.Connect.asyncRequest('GET', '/data/ui/trigger', triggerHandler);
};

var oButtonRun = new YAHOO.widget.Button({ 
    id: "button_run",  
    type: "split", 
    label: "Submit", 
    container: "toolbar",
    menu: submitMenu
});
YAHOO.util.Event.addListener("file_upload", 'click', function() { UploadDlg(); });
YAHOO.util.Event.addListener("run_trigger", 'click', function() { onTrigger(); });

var oButtonSave = new YAHOO.widget.Button({ 
    id: "button_save",  
    type: "push",  
    label: "Save", 
    container: "toolbar"  
}); 
YAHOO.util.Event.addListener("button_save", 'click', function() { jsBox.register(); });

var oButtonExport = new YAHOO.widget.Button({ 
    id: "button_export",  
    type: "push",  
    label: "Export", 
    container: "toolbar"  
});
YAHOO.util.Event.addListener("button_export", 'click', function() {
        myPanel = new YAHOO.widget.Panel("exportWindow", { 
        width:"600px",
        modal: true,
        fixedcenter: true,  
        constraintoviewport: true,  
        close:true,  
        draggable:true} ); 
    
    var jsonConfig = YAHOO.lang.JSON.stringify(jsBox.jsBoxLayer.getWiring())//.replace(/},{/g, "},\n{");        
    myPanel.setHeader("Export Project Configuration"); 
    myPanel.setBody( "<div style='overflow:auto;'>" + jsonConfig + "</div>" );
    myPanel.setFooter("Copy and paste the output above or send this configuration via <a href=\"mailto:?body=" + escape(jsonConfig) + "&subject=Pypes Configuration File\">email</a>");
    myPanel.render(document.body);
    myPanel.show();
});
        
var aboutDialog = new function AboutDialog() {
    this.aboutPanel = new YAHOO.widget.SimpleDialog("aboutDialog", {
        width: "320px",
        zIndex: 25,
        modal: true,
        fixedcenter: true,
        visible: false,
        draggable: true,
        close: true,
        constraintoviewport: true,
        buttons: [{ text:"OK", handler:function() {this.hide();}}]
    });
    this.aboutPanel.setHeader("About");
    this.aboutPanel.setBody("<center><img src=\"/images/PypesLogoWhite.png\" /><br><br><b>Pypes 1.1.0</b><br><br>A component based data flow framework based on Stackless Python.<br><br>Copyright &copy; 2009-2010<br><a target=\"_blank\" href=\"http://www.pypes.org\">http://www.pypes.org</a><br></center>");
    this.aboutPanel.render(document.body);
    this.show = function() { this.aboutPanel.show(); };
};

var oButtonAbout = new YAHOO.widget.Button({ 
    id: "button_about",  
    type: "push",  
    label: "About",
    container: "toolbar"  
});
YAHOO.util.Event.addListener("button_about", "click", function() { aboutDialog.show(); } );

var oButtonSignout = new YAHOO.widget.Button({ 
    id: "button_signout",  
    type: "push",  
    label: "Sign Out", 
    container: "toolbar"  
}); 
YAHOO.util.Event.addListener("button_signout", 'click', function() {window.location.href="/signout";});
