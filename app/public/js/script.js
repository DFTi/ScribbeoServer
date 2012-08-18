// ---------------- Global
var sanitize_fs_name = function(input) {
  return input.replace(/[\W]/g, '-');
}

var flash = function(notError, message) {
  if (notError) {
    $("#flash .errors").html('');
    $("#flash .notice").html(message);
  } else {
    $("#flash .notice").html('');
    $("#flash .errors").html(message);
  }
  $('#flash div').show();
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
    if (typeof(res["file_deletion"])!="undefined") { // file deletion
      toBeRemoved = $('li.fileItem[data-filename="'+res['filename']+'"]');
    } else if (typeof(res["count"])!="undefined") { // type: permission
      console.log('deleted a permission');
      $(listItem).find('.userCount').text(res["count"]);
      if (listItem.children('.permittedUsers').children().size() == 1)
        toBeRemoved = listItem.children('.permittedUsers');
      else
        toBeRemoved = listItem.find('.permittedUser[data-id="'+res['user_id']+'"]');
    } else if (type == "folder") {
      console.log('deleted a folder');
    } else if (type == "user") {
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
    var message;
    if (type=="folder") {
      message = "Are you sure you want to remove this folder? Permissions will be lost, however the folder is not removed from disk. You may always add it again later."
    } else if (type=="file") {
      message = "Are you sure you want to DELETE '"+$(this).siblings('span').text()+"'? There is no undo!"
    } else {
      message = "Are you sure you want to remove this "+type+"?";
    }

    if (!confirm(message)) return;
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
  var itemCount = $(folderItem).size();
  if (itemCount > 1) {// more than one item to bind
    $(folderItem).each(function(i){
      bindFolderItem($(folderItem)[i]);
    });
    return;
  } else if (itemCount === 0) return;
  // user counter toggle
  userCounts = $(folderItem).find('.userCount');
  userCounts.click(function () {
    userCount = $(this);
    if (userCount.text() == "0") return;
    userCount.siblings('.permittedUsers').toggle(0, function (){
      if ($(this).is(':visible')) {
        console.log(userCount);
        userCount.addClass('showingChildren');
      } else
        userCount.removeClass('showingChildren');
    });
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
            newFolderItem.find('.userCount').addClass('showingChildren');
          }
          folder.replaceWith(newFolderItem);
          bindFolderItem(newFolderItem);
          newFolderItem.find('.folderUserInfo').animateHighlight('green', 1000);
          flash(true, res["message"]);
        } else {
          folder.find('.folderUserInfo').animateHighlight('red', 1000);
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

// ------------------ Apple switch

var AppleSwitchToggle = function (input) {
  var checked = input.is(':checked');
  if (checked) {
    input.prop('checked', false);
    input.parent().removeClass('on');
  } else {
    input.prop('checked', true);
    input.parent().addClass('on');
  }
  return !checked;
};

var AppleSwitchHandler = function () {
  var checked = AppleSwitchToggle($(this).children('input'));
  var url = $(this).attr('data-url');
  if (typeof(url) != 'undefined') {
    console.log('posting');
    $.post(url, {'checked':checked}, function (res) {
      if (res['success']) {
        // console.log('it worked');
        console.log(res['checked']);
      } else {
        // console.log('it failed, revert the button and display the error');
      }
    });
  }
};

// -------------------- update button

var SaveButtonHandler = function () {
  var input = $(this).siblings('input');
  var url = $(this).attr('data-url');
  $.post(url, {'value':input.val()}, function (res) {
    if (res['success']) {
      console.log('it worked');
    } else {
      // display an error if necessary
    }
  });
};

// ---------------------
// Change password
function bind_change_password() {
  $('a#changePassword').click(function () {
    $('#changePass').toggle();
    return false;
  });

  $('#changePass #cancel').click(function () {
    $('#changePass input').val('');
    $('#changePass').hide();
  });

  $('#changePass #submit').click(function () {
    var data = {
      "user":{
        "old_password":$(this).siblings('#curPass').val(),
        "password":$(this).siblings('#newPass').val(),
        "confirmation":$(this).siblings('#newPassConf').val()
      }
    };
    $.post($(this).attr('data-url'), data, function(res) {
      if(typeof(res['success'] != 'undefined')){
        alert(res['success']);
        $('#changePass').fadeOut('slow');
      } else {
        alert(res['errors']);
      }
    });
  });
}

//
//  READY
//

$(function () {
  // Manage Contents Page
  bindDeleteButtonPost('file', $('.fileItem .deleteButton'));  

  bind_change_password();

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
          sanitize_fs_name(newEntry.find('input#folderName').val()),
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

  
  // Server Settings Panel Bindings

  $('.switch').click(AppleSwitchHandler);
  $('button.save').click(SaveButtonHandler);

});



