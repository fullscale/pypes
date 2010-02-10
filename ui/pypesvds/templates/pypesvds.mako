<?xml version="1.0" encoding="UTF-8"?>
<html>
 <head>
  <title>Pypes - Visual Design Studio</title>
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <link rel="stylesheet" type="text/css" href="/css/toolbar.css">
    <link rel="stylesheet" type="text/css" href="/css/tree.css">
    <link rel="stylesheet" type="text/css" href="/css/layout.css" />
    <link rel="stylesheet" type="text/css" href="/css/WireIt.css" />

    <!-- YUI -->
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/reset/reset-min.css" />
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/fonts/fonts-min.css" /> 
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/menu/assets/skins/sam/menu.css">
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/button/assets/skins/sam/button.css" />
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/fonts/fonts.css">
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/container/assets/skins/sam/container.css">
    <link rel="stylesheet" type="text/css" href="/js/yui-2.6.0/build/assets/skins/sam/resize.css" /> 

  </head>
     <body style="width:100%; height:100%; background-color:#ffffff;" class="yui-skin-sam">
        <div id="top1">
            <div style="background-color:#ec3b97; height:2px;"></div>
            <div id="toolbar"></div>
        </div> 

        <div id="bottom1"> </div> 

        <div id="left1">
            <div id="tree" style="width:97%; padding-left:10px; padding-top:10px; float:right; background-color:#ebebeb; height:97%; overflow-y:auto;"><p></p></div>
        </div> 

        <div id="center1">
            <div id="wirelayer" style="" ></div>
        </div> 
    </body>
</html>

<div id="proxy" class="WireIt-Container" style="opacity:0.4; left:618px; top:184px; visibility:hidden;">
    <div class="WireIt-Container-ddhandle"></div>
    <div class="body">
        <textarea style="text-align:center;width:100%;height:30px; border-top-width;1px; border-right-width:1px; border-bottom-width:1px; border-left-width:1px; border-style:initial; border-color:initial; padding-top:5px; padding:5px; resize:none; overflow:hidden; font-style:italic;">Dragging...</textarea>
    </div>
    <div class="WireIt-Container-resizehandle"></div>
    <div class="WireIt-Container-closebutton"></div>
    <div class="WireIt-Container-configbutton"></div>
 </div>

<script type="text/javascript" src="/js/yui-2.6.0/build/yuiloader/yuiloader-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/event/event-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/connection/connection-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/dom/dom-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/treeview/treeview-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/element/element-beta-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/button/button-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/utilities/utilities.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/container/container-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/json/json-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/yahoo/yahoo-min.js"></script>
<script type="text/javascript" src="/js/yui-2.6.0/build/menu/menu-min.js"></script>

<script src="/js/yui-2.6.0/build/resize/resize-min.js"></script> 
<script src="/js/yui-2.6.0/build/yahoo-dom-event/yahoo-dom-event.js"></script>
<script src="/js/yui-2.6.0/build/layout/layout-min.js"></script>
<script src="/js/yui-2.6.0/build/dragdrop/dragdrop-min.js"></script>
<!-- http://yui.yahooapis.com/2.6.0/build/ -->
<!-- Excanvas -->
<!--[if IE]><script type="text/javascript" src="/excanvas.js"></script><![endif]-->

<!-- WireIt -->
<script type="text/javascript" src="/js/wireit/WireIt.js"></script>
<script type="text/javascript" src="/js/wireit/CanvasElement.js"></script>
<script type="text/javascript" src="/js/wireit/Wire.js"></script>
<script type="text/javascript" src="/js/wireit/Terminal.js"></script>
<script type="text/javascript" src="/js/wireit/util/DD.js"></script>
<script type="text/javascript" src="/js/wireit/util/DDResize.js"></script>
<script type="text/javascript" src="/js/wireit/Container.js"></script>
<script type="text/javascript" src="/js/wireit/Layer.js"></script>
<script type="text/javascript" src="/js/wireit/LayerMap-beta.js"></script>

<script type="text/javascript" src="/js/ApplicationLayout.js"></script>
<script type="text/javascript" src="/js/ApplicationMain.js"></script>
<script type="text/javascript" src="/js/ApplicationToolbar.js"></script>
<script type="text/javascript" src="/js/ApplicationTree.js"></script>
