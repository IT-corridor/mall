var dialogs = {};
var pending_friends = [];

function onSystemMessageListener(message) {
    if (!message.delay) {
        switch (message.extension.notification_type) {
            case "1":
                // This is a notification about dialog creation
                getAndShowNewDialog(message.extension.dialog_id);
                break;
            case "2":
                // This is a notification about dialog update
                getAndUpdateDialog(message.extension.dialog_id);
                break;
            default:
                break;
        }
    }
}

function retrieveChatDialogs() {
    // get the chat dialogs list
    //
    QB.chat.dialog.list(null, function (err, resDialogs) {
        if (err) {
            console.log(err);
        } else {

            // repackage dialogs data and collect all occupants ids
            //
            var occupantsIds = [];

            if (resDialogs.items.length === 0) {

                // hide login form
                $("#loginForm").modal("hide");

                // setup attachments button handler
                //
                $("#load-img").change(function () {
                    var inputFile = $("input[type=file]")[0].files[0];
                    if (inputFile) {
                        $("#progress").show(0);
                    }

                    clickSendAttachments(inputFile);
                });

                return;
            }

            resDialogs.items.forEach(function (item, i, arr) {
                var dialogId = item._id;
                dialogs[dialogId] = item;

                // join room
                if (item.type != 3) {
                    QB.chat.muc.join(item.xmpp_room_jid, function () {
                        console.log("Joined dialog " + dialogId);
                    });
                }

                item.occupants_ids.map(function (userId) {
                    occupantsIds.push(userId);
                });
            });

            // load dialogs' users
            //
            updateDialogsUsersStorage(jQuery.unique(occupantsIds), function () {
                // show dialogs
                //
                resDialogs.items.forEach(function (item, i, arr) {
                    showOrUpdateDialogInUI(item, false);
                });

                //  and trigger the 1st dialog
                //
                triggerDialog(resDialogs.items[0]._id);

                // hide login form
                $("#loginForm").modal("hide");

                // setup attachments button handler
                //
                $("#load-img").change(function () {
                    var inputFile = $("input[type=file]")[0].files[0];
                    if (inputFile) {
                        $("#progress").show(0);
                        $(".input-group-btn_change_load").addClass("visibility_hidden");
                    }

                    clickSendAttachments(inputFile);
                });
            });
        }
    });
}

function showOrUpdateDialogInUI(itemRes, updateHtml) {
    var dialogId = itemRes._id;
    var dialogName = itemRes.name;
    var dialogType = itemRes.type;
    var dialogLastMessage = itemRes.last_message;
    var dialogUnreadMessagesCount = itemRes.unread_messages_count;
    var dialogIcon = getDialogIcon(itemRes.type);

    if (dialogType == 3) {
        opponentId = QB.chat.helpers.getRecipientId(itemRes.occupants_ids, currentUser.id);
        opponentLogin = getUserLoginById(opponentId);
        dialogName = 'Dialog with ' + opponentLogin;
    }

    if (updateHtml === true && $('#' + dialogId).length < 1) {
        var updatedDialogHtml = buildDialogHtml(dialogId, dialogUnreadMessagesCount, dialogIcon, dialogName, dialogLastMessage);
        $('#dialogs-list').prepend(updatedDialogHtml);
        console.log('116@@@');
        $('.list-group-item.active .badge').text(0).hide(0);
    } else {
        var dialogHtml = buildDialogHtml(dialogId, dialogUnreadMessagesCount, dialogIcon, dialogName, dialogLastMessage);
        $('#dialogs-list').append(dialogHtml);
        console.log('121@@@');
    }
}

// add photo to dialogs
function getDialogIcon(dialogType) {
    var groupPhoto = '<img src="'+resource_url+'images/ava-group.svg" width="30" height="30" class="round">';
    var privatPhoto = '<img src="'+resource_url+'images/ava-single.svg" width="30" height="30" class="round">';
    var defaultPhoto = '<span class="glyphicon glyphicon-eye-close"></span>';

    var dialogIcon;
    switch (dialogType) {
        case 1:
            dialogIcon = groupPhoto;
            break;
        case 2:
            dialogIcon = groupPhoto;
            break;
        case 3:
            dialogIcon = privatPhoto;
            break;
        default:
            dialogIcon = defaultPhoto;
            break;
    }
    return dialogIcon;
}

// show unread message count and new last message
function updateDialogsList(dialogId, text) {

    // update unread message count
    var badgeCount = $('#' + dialogId + ' .badge').html();
    $('#' + dialogId + '.list-group-item.inactive .badge').text(parseInt(badgeCount) + 1).fadeIn(500);

    // update last message
    $('#' + dialogId + ' .list-group-item-text').text(stickerpipe.isSticker(text) ? 'Sticker' : text);
}

// Choose dialog
function triggerDialog(dialogId) {
    console.log("Select a dialog with id: " + dialogId + ", name: " + dialogs[dialogId].name);

    // deselect
    var kids = $('#dialogs-list').children();
    kids.removeClass('active').addClass('inactive');

    // select
    $('#' + dialogId).removeClass('inactive').addClass('active');

    $('.list-group-item.active .badge').text(0).delay(250).fadeOut(500);

    $('#messages-list').html('');

    // load chat history
    //
    retrieveChatMessages(dialogs[dialogId], null);

    $('#messages-list').scrollTop($('#messages-list').prop('scrollHeight'));
}


function showNewDialogPopup() {
  var full_name = prompt("Opponent's name : ");
  if (full_name != null) {
    if (full_name.length < 3)
      full_name += '_';
    if (full_name.length < 3)
      full_name += '_';

    QB.users.get({full_name: full_name}, function(err, result) {
      if (err) {
        console.log(err);
        alert("Oops! Name is wrong!\nPlease check it again.");
      } else {
        // console.log(result);
        console.log(result.items[0].user);
        console.log('retrieveUsers@@@@');
        var opponent = result.items[0].user;
        var endpoint = server_url+'/api/v1/notification/';
        // console.log(document.cookie);

        pending_friends.push(opponent);
        console.log(pending_friends);

        $.ajax({
            'url': endpoint,
            'data': {'type': 'chat_request', 'message': currentUser.full_name + ' wants to chat with you!@'+currentUser.login, 'user_id': opponent.login},
            'type': 'POST',
            'beforeSend': function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function () {
                alert('Request is sent successfully!');
            }
        });
      }      
    });  
    }
}

// select users from users list
function clickToAdd(forFocus) {
    if ($('#' + forFocus).hasClass("active")) {
        $('#' + forFocus).removeClass("active");
    } else {
        $('#' + forFocus).addClass("active");
    }
}

function createNewDialog_real(user_id, dialogName) {
    var user_id_qb;
    console.log('Before create a dialog');
    console.log(pending_friends);

    for(var i = 0; i < pending_friends.length; i++) {
        if (pending_friends[i].login == user_id) {
            user_id_qb = pending_friends[i].id;
            break;
        }
    }

    var dialogOccupants = [user_id_qb];
    var params = {
        type: 3,    // private
        occupants_ids: dialogOccupants,
        name: dialogName
    };

    // create a dialog
    //
    console.log("Creating a dialog with params: " + JSON.stringify(params));

    QB.chat.dialog.create(params, function (err, createdDialog) {
        if (err) {
            console.log(err);
        } else {
            console.log("Dialog " + createdDialog._id + " created with users: " + dialogOccupants);

            // save dialog to local storage
            var dialogId = createdDialog._id;
            dialogs[dialogId] = createdDialog;

            currentDialog = createdDialog;

            joinToNewDialogAndShow(createdDialog);

            notifyOccupants(createdDialog.occupants_ids, createdDialog._id, 1);

            triggerDialog(createdDialog._id);

            $('a.users_form').removeClass('active');
        }
    });
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}
//
function joinToNewDialogAndShow(itemDialog) {
    var dialogId = itemDialog._id;
    var dialogName = itemDialog.name;
    var dialogLastMessage = itemDialog.last_message;
    var dialogUnreadMessagesCount = itemDialog.unread_messages_count;
    var dialogIcon = getDialogIcon(itemDialog.type);

    // join if it's a group dialog
    if (itemDialog.type != 3) {
        QB.chat.muc.join(itemDialog.xmpp_room_jid, function () {
            console.log("Joined dialog: " + dialogId);
        });
        opponentLogin = null;
    } else {
        opponentId = QB.chat.helpers.getRecipientId(itemDialog.occupants_ids, currentUser.id);
        opponentLogin = getUserLoginById(opponentId);
        dialogName = chatName = 'Dialog with ' + opponentLogin;
    }

    // show it
    if ($('#' + dialogId).length < 1) {
        var dialogHtml = buildDialogHtml(dialogId, dialogUnreadMessagesCount, dialogIcon, dialogName, dialogLastMessage);
        $('#dialogs-list').prepend(dialogHtml);
        console.log('320@@@');
    }
}

//
function notifyOccupants(dialogOccupants, dialogId, notificationType) {
    dialogOccupants.forEach(function (itemOccupanId, i, arr) {
        if (itemOccupanId != currentUser.id) {
            var msg = {
                type: 'chat',
                extension: {
                    notification_type: notificationType,
                    dialog_id: dialogId
                }
            };

            QB.chat.sendSystemMessage(itemOccupanId, msg);
        }
    });
}

//
function getAndShowNewDialog(newDialogId) {
    // get the dialog and users
    //
    QB.chat.dialog.list({_id: newDialogId}, function (err, res) {
        if (err) {
            console.log(err);
        } else {

            var newDialog = res.items[0];

            // save dialog to local storage
            var dialogId = newDialog._id;
            dialogs[dialogId] = newDialog;

            // collect the occupants
            var occupantsIds = [];
            newDialog.occupants_ids.map(function (userId) {
                occupantsIds.push(userId);
            });
            updateDialogsUsersStorage(jQuery.unique(occupantsIds), function () {

            });

            joinToNewDialogAndShow(newDialog);
        }
    });
}

function getAndUpdateDialog(updatedDialogId) {
    // get the dialog and users
    //

    var dialogAlreadyExist = dialogs[updatedDialogId] !== null;
    console.log("dialog " + updatedDialogId + " already exist: " + dialogAlreadyExist);

    QB.chat.dialog.list({_id: updatedDialogId}, function (err, res) {
        if (err) {
            console.log(err);
        } else {

            var updatedDialog = res.items[0];

            // update dialog in local storage
            var dialogId = updatedDialog._id;
            dialogs[dialogId] = updatedDialog;

            // collect the occupants
            var occupantsIds = [];
            updatedDialog.occupants_ids.map(function (userId) {
                occupantsIds.push(userId);
            });
            updateDialogsUsersStorage(jQuery.unique(occupantsIds), function () {

            });

            if (!dialogAlreadyExist) {
                joinToNewDialogAndShow(updatedDialog);
            } else {
                // just update UI
                $('#' + dialogId + ' h4 span').html('');
                $('#' + dialogId + ' h4 span').append(updatedDialog.name);
            }
        }
    });
}

// show modal window with dialog's info
function showDialogInfoPopup() {
    $("#update_dialog").modal("show");
    $('#update_dialog .progress').hide();

    // shwo current dialog's occupants
    setupDialogInfoPopup(currentDialog.occupants_ids, currentDialog.name);
}

// show information about the occupants for current dialog
function setupDialogInfoPopup(occupantsIds, name) {

    // show name
    $('#dialog-name-input').val(name);

    // show occupants
    var logins = [];
    occupantsIds.forEach(function (item, index) {
        login = getUserLoginById(item);
        logins[index] = login;
    });
    $('#all_occupants').text('');
    $('#all_occupants').append('<b>Occupants: </b>' + logins.join(', '));

    // show type
    //
    // private
    if (currentDialog.type == 3) {
        $('.dialog-type-info').text('').append('<b>Dialog type: </b>privat chat');
        $('.new-info').hide();
        $('.push').hide();
        $('#push_usersList').hide();
        $('#update_dialog_button').hide();

        // group
    } else {
        $('.dialog-type-info').text('').append('<b>Dialog type: </b>group chat');
        $('.new-info').show();
        $('.push').show();
        $('#push_usersList').show();
        $('#update_dialog_button').show();

        // get users to add to dialog
        retrieveUsersForDialogUpdate(function (users) {
            if (users === null || users.length === 0) {
                return;
            }

            $.each(users, function (index, item) {
                var userHtml = buildUserHtml(this.user.full_name, this.user.login, this.user.id, true);
                $('#add_new_occupant').append(userHtml);
            });
        });
        setupScrollHandlerForNewOccupants();
    }
}


function setupScrollHandlerForNewOccupants() {
    // uploading users scroll event
    $('#push_usersList').scroll(function () {
        if ($('#push_usersList').scrollTop() == $('#add_new_occupant').height() - $('#push_usersList').height()) {

            retrieveUsersForDialogUpdate(function (users) {
                if (users === null || users.length === 0) {
                    return;
                }
                $.each(users, function (index, item) {
                    var userHtml = buildUserHtml(this.user.full_name, this.user.login, this.user.id, false);
                    $('#add_new_occupant').append(userHtml);
                });
            });

        }
    });
}

// for dialog update
function onDialogUpdate() {
    var pushOccupants = [];
    $('#add_new_occupant .users_form.active').each(function (index) {
        pushOccupants[index] = $(this).attr('id').slice(0, -4);
    });

    var dialogName = $('#dialog-name-input').val().trim();

    var toUpdate = {
        name: dialogName,
        push_all: {occupants_ids: pushOccupants}
    };

    console.log("Updating the dialog with params: " + JSON.stringify(toUpdate));

    QB.chat.dialog.update(currentDialog._id, toUpdate, function (err, res) {
        if (err) {
            console.log(err);
        } else {
            console.log("Dialog updated");

            var dialogId = res._id;
            dialogs[dialogId] = res;

            currentDialog = res;

            $('#' + res._id).remove();

            showOrUpdateDialogInUI(res, true);

            notifyOccupants(res.occupants_ids, dialogId, 2);

            $('#' + res._id).removeClass('inactive').addClass('active');
        }
    });

    $("#update_dialog").modal("hide");
    $('#dialog-name-input').val('');
    $('.users_form').removeClass("active");
}

// delete current dialog
function onDialogDelete() {
    if (confirm("Are you sure you want remove the dialog?")) {
        QB.chat.dialog.delete(currentDialog._id, function (err, res) {
            // if (err) {
            //     console.log(err);
            // } else {
            console.log("Dialog removed" + currentDialog._id);
            $('#' + currentDialog._id).remove();

            // remove from storage
            delete dialogs[currentDialog._id];

            //  and trigger the next dialog
            if (Object.keys(dialogs).length > 0) {
                triggerDialog(dialogs[Object.keys(dialogs)[0]]._id);
            }

            // }
        });

        $("#update_dialog").modal("hide");
        $('#update_dialog .progress').show();
    }
}
