var cdn_document_url;
var cdn_document_name;

	CKEDITOR.dialog.add( 'cdnDialog', function( editor ) {

	  return {

		title : 'Insertion d\'un lien vers un document du CDN',
		resizable : CKEDITOR.DIALOG_RESIZE_HEIGHT,
		minWidth : 600,
		minHeight : 480,
		contents : [
		  {
			id : "cdn_browse",
			label : 'Sélection du fichier cible',
			title : 'Browse',
			expand : true,
			elements :[
			  {
				id : "iframe_cdn_browse",
				src : "https://uclouvain.be/PPE-filemanager/",
				type : 'iframe',
				label : 'Link to CDN Doc',
				width : '100%',
				height : 480
			  }
			]
		  }
		],
		onOk: function() {
		  if ( cdn_document_url == null ) {
			alert("Vous devez faire une sélection avant de cliquer 'ok'");
			return false;
		  }

		  var sel = editor.getSelection();
		  var selectedText = sel.getSelectedText();

		  var re = /(?:\.([^.]+))?$/;
		  var ext = re.exec(cdn_document_name)[0];
		  var is_image = ext.match(/.(jpg|jpeg|png|gif)$/i);
		  var has_selected_text = selectedText != null && selectedText.length != 0;

		  var link;

		  if (is_image && !has_selected_text){
		  	link = editor.document.createElement('img');
		  	link.setAttribute('src', cdn_document_url);
		  	link.setAttribute('alt', cdn_document_name);
		  }
		  else {
		  	  link = editor.document.createElement('a');
			  if (has_selected_text) link.setHtml(selectedText);
			  else {
				  if (cdn_document_name != null && cdn_document_name.length != 0) link.setHtml(" " + cdn_document_name);
			  }

			  link.setAttribute('href', cdn_document_url);
			  link.setAttribute('target', '_blank');
			  if (cdn_document_name != null) link.setAttribute('title', cdn_document_name);
		  }
		  editor.insertElement(link);

		}
	  }

	});



//
// automatic dialog re size  feature
//
	CKEDITOR.dialog.on('resize', function (evt) {

	  var dialog = CKEDITOR.dialog.getCurrent();
	  if ( dialog ) {
		dialog = dialog._.contents;
		var BrowseIframeId = dialog.cdn_browse.iframe_cdn_browse._.frameId;
		var instanceBrowse = document.getElementById(BrowseIframeId);
		instanceBrowse.style.height = evt.data.height + 'px';
		instanceBrowse.style.width = evt.data.width + 'px';
	  }
	});