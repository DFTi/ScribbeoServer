$().ready(function () {
  // ---------------- Global
  var flash = function(notError, message) {
    if (notError) {
      $("#flash .errors").html('');
      $("#flash .notice").html(message);
    } else {
      $("#flash .notice").html('');
      $("#flash .errors").html(message);
    }
    setTimeout(function () {
      $("#flash div").fadeOut('slow');
    }, 5000);
  };

  // Admin ---------------- Dashboard & Panels

  var resetForm = function (element) {
    element.find(".errors").html('');
    inputs = element.children('input');
    inputs.each(function (i) { $(inputs[i]).val(''); });
    element.siblings('.addButton').removeClass('cancelButton').text('Add');
    return element;
  };
  
  $("li.entryForm input").keydown(function (event){
    if (event.which == 13) {
      $(this).siblings(".submitButton").click();
    }
  });

  $('.addButton').click(function () {
    var newEntry = $(this).siblings('.entryForm');
    if (newEntry.is(':visible')) {
      resetForm(newEntry);
    } else {
      $(this).addClass('cancelButton').text('Cancel');
    }
    newEntry.fadeToggle('fast');
  });
  
  $('.submitButton').click(function () {
    var newEntry = $(this).parent();
    var type = newEntry.attr('data-type');
    var data = {};
    if (type == 'folder') {
      data['folder'] = {
        'name':
          newEntry.find('input#folderName').val(),
        'path':
          newEntry.find('input#folderPath').val()
      };
    } else
    if (type == 'user') {
      data['user'] = {
        'username':newEntry.find('input#username').val(),
        'password':newEntry.find('input#password').val(),
        'confirmation':newEntry.find('input#confirmation').val()
      };
    }
    $.post($(this).attr('data-url'), data, function (res) {
      if (res['success']) {
        if (newEntry.siblings('.placeholder'))
          newEntry.siblings('.placeholder').remove();
        html = $(res['html']).css('display', 'none');
        html.insertAfter(newEntry).fadeToggle('slow');
        resetForm(newEntry).hide();
        // Make the bindings:
        var type = newEntry.attr('data-type');
        if (type == 'folder') {
          bindUserCounterToggle($(html).find('.userCount'));
          makeFolderItemDroppable($(html));
          bindDeleteButtonPost('folder', $(html).find(".deleteButton"));
        } else
        if (type == 'user') {
          console.log('binding user');
          makeUserIconDraggable($(html).find('.icon'));
          bindDeleteButtonPost('user', $(html).find(".deleteButton"));
        }
      } else {
        newEntry.find(".errors").html(res["errors"]);
      }
    });
  });
  
  var bindDeleteButtonPost = function (type, div) {
    $(div).click(function () {
      if (!confirm("Are you sure you want to delete this "+type+"? You cannot undo this action.")) return;
      var listItem;
      var toBeRemoved;
      var data = {
        "id":$(this).parent().attr('data-id')
      };
      if (type=="permission") {
        listItem = $(this).parents("li.entry");
        data["folder_id"] = $(this).parents('li.entry.folder').attr('data-id');
        
        console.log($(this));
        console.log($(this).parents('.permittedUsers').size());
        if ($(this).parents('.permittedUsers').children().size() == 1)
          toBeRemoved = $(this).parents('.permittedUsers');
        else
          toBeRemoved = $(this).parents('.permittedUser');
      } else {
        toBeRemoved = $(this).parents("li.entry");
      }
      $.post($(this).attr('data-url'), data, function (res) {
        if (res["success"]) {
          if (type=="permission") {
            $(listItem).find('.userCount').text(res["count"]);
          } else if (type == "user") {
            // they may have been removed from folders
            // better to reload that whole panel
            $.get($('.panel#folders').attr('data-url'), function (fRes) {
              $('#folders.panel').html(fRes["html"]);
            });
          }
          console.log(toBeRemoved); // --------
          toBeRemoved.fadeOut('fast', function () {
            toBeRemoved.remove();
          });
        } else {
          flash(false, 'Could not remove '+type);
        }
      });
    });
  };
  
  var bindUserCounterToggle = function (li) {
    $(li).click(function () {
      count = parseInt($(this).text(), 10);
      if (count > 0)
        $(this).siblings('.permittedUsers').fadeToggle('fast');
    });
  };
  
  var makeUserIconDraggable = function (li) {
    $(li).draggable({'revert':true});
  };

  var replaceFolderEntry = function (old, htmlEl) {
    var newFolderItem = $(htmlEl);
    if ($(old).find('.permittedUsers').is(':visible')) {
      newFolderItem.find('.permittedUsers').
      show().css('display', 'block');
    }
    old.replaceWith(newFolderItem);
    bindUserCounterToggle(newFolderItem.find('.userCount'));
    makeFolderItemDroppable(newFolderItem);
    bindDeleteButtonPost('permission', newFolderItem.find(".revokeButton"));
  };

  var makeFolderItemDroppable = function (li) {
    $(li).droppable({
      drop: function( event, ui ) {
        var folder = $(this);
        $.post($("#addPermission").val(), {
          "user_id":$(ui['draggable']).parent().attr('data-id'),
          "folder_id":folder.attr('data-id')
        }, function (res) {
          if (res['success']) {
            replaceFolderEntry(folder, res['html']);
            flash(true, res["message"]);
          } else {
            flash(false, res["errors"]);
          }
        });
      }
    });
  };
  
  makeUserIconDraggable(".entry.user .icon");
  bindUserCounterToggle(".entry.folder .userCount");
  makeFolderItemDroppable(".entry.folder");

  bindDeleteButtonPost('user', '.entry.user .deleteButton');
  bindDeleteButtonPost('folder', '.entry.folder .deleteButton');
  bindDeleteButtonPost('permission', '.entry.folder .revokeButton');

});



