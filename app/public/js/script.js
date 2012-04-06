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

var folderItem = function (id) {
  return $('li.entry[data-id="'+String(id)+'"]');
};

// ----------------------

var refetchFolderPanel = function () {
  $.get($('.panel#folders').attr('data-url'), function (fRes) {
    $('#folders.panel').html(fRes["html"]);
  });
  console.log('refetch and rebind folder panel');
  setTimeout(function () {
    bindFolderItem('li.entry.folder');
  }, 150);
};

var deleteResponseHandler = function (res) {
  var listItem = $('li.entry[data-id="'+res['id']+'"]');
  var type = listItem.attr('data-type');
  var toBeRemoved = listItem;
  if (res["success"]) {
    if (typeof(res["count"])!="undefined") { // type: permission
      console.log('deleted a permission');
      $(listItem).find('.userCount').text(res["count"]);
      if (listItem.children('.permittedUsers').children().size() == 1)
        toBeRemoved = listItem.children('.permittedUsers');
      else
        toBeRemoved = listItem.find('.permittedUser[data-id="'+res['user_id']+'"]');
    } else
    if (type == "folder") {
      console.log('deleted a folder');
    } else
    if (type == "user") {
      console.log('deleted a user');
      refetchFolderPanel();
    }
    toBeRemoved.fadeOut('fast', function () {
      console.log('to be removed: ');
      console.log(toBeRemoved);
      toBeRemoved.remove();
    });

  } else
    flash(false, 'Could not remove '+type);
};

var bindDeleteButtonPost = function (type, div) {
  $(div).click(function () {
    if (!confirm("Are you sure you want to delete this "+type+"? You cannot undo this action.")) return;
    var data = {
      "id":$(this).parent().attr('data-id')
    };
    if (type=="permission")
      data["folder_id"] = $(this).parents('li.entry.folder').attr('data-id');
    $.post($(this).attr('data-url'), data, deleteResponseHandler);
  });
};

var bindUserItem = function (userItem) {
  $(userItem).find(".icon").draggable({'revert':true});
  bindDeleteButtonPost('user', $(userItem).find('.deleteButton'));
};

// ----------------------

var bindFolderItem = function (folderItem) {
  if ($(folderItem).size() > 1) {// more than one item to bind
    $(folderItem).each(function(i){
      bindFolderItem($(folderItem)[i]);
    });
    return;
  }
  console.log("Binding Folder Item ID: "+$(folderItem).attr('data-id'));
  // user counter toggle
  $($(folderItem).find('.userCount')).click(function () {
    count = parseInt($(this).text(), 10);
    if (count > 0)
      $(this).siblings('.permittedUsers').fadeToggle('fast');
  });
  
  bindDeleteButtonPost('folder', $(folderItem).find(' .deleteButton'));
  bindDeleteButtonPost('permission', $(folderItem).find(' .revokeButton'));


  $(folderItem).droppable({
    drop: function( event, ui ) {
      console.log("Droppable: ");

      console.log(this);

      var folder = $(this);
      $.post($("#addPermission").val(), {
        "user_id":$(ui['draggable']).parent().attr('data-id'),
        "folder_id":folder.attr('data-id')
      }, function (res) {
        if (res['success']) {
          var newFolderItem = $(res['html']);
          if ($(folder).find('.permittedUsers').is(':visible')) {
            newFolderItem.find('.permittedUsers').
            show().css('display', 'block');
          }
          folder.replaceWith(newFolderItem);
          bindFolderItem(newFolderItem);
          flash(true, res["message"]);
        } else {
          flash(false, res["errors"]);
        }
      });
    }
  });
};

// ------------------

var resetForm = function (element) {
  element.find(".errors").html('');
  inputs = element.children('input');
  inputs.each(function (i) { $(inputs[i]).val(''); });
  element.siblings('.addButton').removeClass('cancelButton').text('Add');
  return element;
};

//
//  READY
//

$(function () {
  $('a#changePassword').click(function () {
    alert('Not yet implemented. You\'re stuck with it for now.');
    return false;
  });

  // Admin ---------------- Dashboard & Panels
  
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
      console.log(newEntry.children('input[type=text]').first());
      setTimeout(function () {
        newEntry.children('input[type=text]').first().select();
      }, 20);
    }
    newEntry.fadeToggle('fast');
  });
  
// --------------------------

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
        listItem = $(res['html']).css('display', 'none');
        listItem.insertAfter(newEntry).fadeToggle('slow');
        resetForm(newEntry).hide();
        var type = newEntry.attr('data-type');
        if (type == 'folder') {
          setTimeout(function () {
            console.log(listItem);
            bindFolderItem(listItem);
          }, 150);
          //
        } else
        if (type == 'user') {
          console.log('binding user');
          bindUserItem(listItem);
        }
      } else {
        newEntry.find(".errors").html(res["errors"]);
      }
    });
  });
  bindUserItem('.entry.user');
  bindFolderItem('.entry.folder');
});



