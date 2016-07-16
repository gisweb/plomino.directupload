(function ($) {
    "use strict";

    $(function () {

        $('.directupload, .iol-multi-upload-doc').prepOverlay(
            {
                subtype: 'ajax',
                filter: common_content_filter,
                config: {  
               
                    onLoad: function(arg){
                        var me = this;
                        config_upload_form();

                        /*SOVRASCRIVO LA CONFIGURAZIONE GLOBALE CON QUELLA LOCALE*/
                        if($('#fileupload').data('fileType')){
                            var fileType = $('#fileupload').data('fileType').replace(' ', '').replace(',', '|')
                            $('#fileupload').fileupload('option', {
                                acceptFileTypes: new RegExp('(\\.|\/)('+$('#fileupload').data('fileType')+')$', 'i')
                            });
                        }
                        if($('#fileupload').data('maxSize')){
                            $('#fileupload').fileupload('option', {
                                maxFileSize: $('#fileupload').data('maxSize')
                            });
                        }

                        /*EVENTI SU UPLOAD*/
                        $('#fileupload')
                          .bind('fileuploadsubmit', function (e, data) {
                              var inputs;
                              if(data.context){
                                  inputs = data.context.find(':input');
                              }else{
                                  inputs = data.form.find(':input');
                              }
                              if (inputs.filter('[required][value=""]').first().focus().length) {
                                  return false;
                              }
                              data.formData = inputs.serializeArray();
                            })
                          .bind('fileuploadalways', function (e, data) {
                            //console.log("DDDDDDDDDDDDd")
                            //boh...
                          })
                          .bind('fileuploaddone', function (e, data) {
                            //console.log(data.context.first(".preview"))
                            //console.log(data.files)
                            //console.log("FATTO")
                            //console.log(self)
                            //me.getClosers().click()
                            if(data.files.length){
                              var ftype = data.files[0].type
                              if (ftype=="application/pdf"){
                                //SOSTITUIRE CON IMMAGINE PDF
                                //console.log(data.context)
                              }

                            }

                            //console.log(data.result.files)
                            //elenco legato al campo
                            var info = data.result.files[0]
                            //console.log(info)
                            var $el = $("#"+info["field_name"]+"-list");
                            //console.log($el)

                            $el.append('<li><a href="deleteAttachmentIol?field=' + info["field_name"] + '&amp;filename=' + info["name"] + '">\
                                <img src="++resource++plomino.directupload/images/trash.png" alt="Elimina allegato"></a>\
                                <a target="new" href="getfile?filename=' + info["name"] + '">\
                                <img src="topic_icon.png"><span>' + info["name"] + '</span></a></li>')
                            
        /*                    $el.append(
                                $('<li>').append(
                                    $('<a>').attr('href',info["url"]).append(
                                        $('<span>').attr('class', 'tab').append(info["name"])
                            ))); */  



                 

                          });



                    }
                }
            }
        );


        $(document).on("click","a.removeattachment", function(e){
            e.preventDefault();
            var serviceUrl = $(this).data("url");
            if (!confirm("Eliminare il file allegato?"))
                return;
            $.ajax({
                'url':serviceUrl,
                'type':'GET',     
                'dataType':'JSON',     
                'success':function(data, textStatus, jqXHR){
                    console.log(data)
                    var icons = data["icons"];
                    var filename, fileicon;
                    var $el = $("#"+data["fieldname"]+"-list");
                    $el.empty();
                    $.each(data["files"],function(filename,type){
                        fileicon = icons[type] || icons["default"]
                        $el.append('<li><a class="removeattachment" data-url="@@removeattachment?fieldname=' + data["fieldname"] + '&filename=' + filename + '" href="#"><img src="++resource++plomino.directupload/images/trash.png" alt="Elimina allegato"></a>\
                            <a target="new" href="getfile?filename=' + filename + '">\
                            <img src="'+ fileicon +'"><span>' + filename + '</span></a></li>');

                    })

                } 
            })

        });


        /*#######TENTATIVO DI GENERAZIONE DEI DOCUMENTI IN AJAX DA RIVEDERE ##################*/
        $(".iol-wait-doc").each(function(index){

            var fieldName = $(this).attr("name");

            //if(typeof(iol_document_url)=='undefined')
                //return;
            
            //var serviceUrl = iol_document_url + "/createdocx";
            var serviceUrl = $(this).data("serviceUrl");
            var group = $(this).data("group");
            var model = $(this).data("model");
            var pdf = $(this).data("pdf") || 0;
            var printForm = $(this).data("printform") || '';

            var data={
                "field":fieldName,
                "model":model,
                "grp":group,
                "pdf":pdf,
                "printForm":printForm
            }

            $.ajax({
                'url':serviceUrl,
                'type':'GET',     
                'data':data,
                'dataType':'JSON',     
                'success':function(data, textStatus, jqXHR){
                  console.log(data)

                    $("#" + fieldName + "-createdoc").removeClass("iol-wait-doc");
                    $("#" + fieldName + "-createdoc").addClass("iol-download-doc");
                    $("#" + fieldName + "-download").attr("href","getfile?filename=" + data.fileName)


                } 
            })

          });
      
    });


})(jQuery);
